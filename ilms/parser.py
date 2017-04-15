import re
from datetime import datetime

# from html2text import html2text
from bs4 import BeautifulSoup

from ilms import exception


class ParseResult:

    def __init__(self, body=None):
        self.soup = BeautifulSoup(body, 'lxml') if body else None
        self.result = []
        self.extra = {}

pad = ['', ' ', '  ', '   ', ]


def need_login_check(f):
    def wrap(body, *args, **kwargs):
        if '權限不足' in body or 'No Permission!' in body:
            raise exception.PermissionDenied('尚未登入')
        return f(body, *args, **kwargs)
    return wrap


def parse_zh_en_course_name(course_name):
    course_name_en = re.findall('[A-Za-z()0-9 ]+', course_name)[-1]
    course_name_zh = course_name.replace(course_name_en, '')
    return {'en': course_name_en, 'zh': course_name_zh}


def fix_course_id_padding(course_id):
    dept = re.search('[A-Z]+', course_id).group()
    dept_padded = dept + pad[4 - len(dept)]
    return course_id.replace(dept, dept_padded)


def parse_datetime(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')


@need_login_check
def parse_profile(body):
    pr = ParseResult(body)
    name = pr.soup.select_one('#fmName').get('value')
    email = pr.soup.select_one('#fmEmail').get('value')
    pr.result = {'name': name, 'email': email}
    return pr


@need_login_check
def parse_course_list(body):
    pr = ParseResult(body)
    mnu = pr.soup.select('.mnu')[0]
    course_url_regex = re.compile('/course/(\d+)')

    for item in mnu.select('.mnuItem'):
        course_a = item.find('a')
        match = course_url_regex.match(course_a.get('href'))
        if not match:
            continue
        course_id = re.sub('[()]', '', item.find('span').text)
        pr.result.append({
            'id': match.group(1),
            'name': parse_zh_en_course_name(course_a.text),
            'course_id': course_id  # fix_course_id_padding(course_id)
        })
    return pr


@need_login_check
def parse_homework_list(body):
    pr = ParseResult(body)
    main = pr.soup.select_one('#main')
    if '目前尚無資料' in main.text:
        return pr

    for row in main.select('tr')[1:]:
        td = row.find_all('td')
        href = td[1].select_one('a').get('href')
        date = td[4].find('span').get('title')
        pr.result.append({
            'id': re.match('.*hw=(\d+).*', href).group(1),
            'title': td[1].text.strip(),
            'date_string': date,
            'date': parse_datetime(date)
        })
    return pr


@need_login_check
def parse_homework_detail(body):
    pr = ParseResult(body)
    tr = pr.soup.select('tr')

    def trs_helper(trs):
        for row in trs:
            k, v = row.select('td')
            yield k.text, v.text

    pr.result = {'title': pr.soup.select_one('#main span.curr').text.strip()}
    pr.result['extra'] = {
        k: v
        for i, (k, v) in enumerate(trs_helper(tr))
        if i not in [0, 5, 6, 7]
        # header, date, description, attachments
    }

    date = tr[5].select('td')[1].text + ':00'
    pr.result['date_string'] = date
    pr.result['date'] = parse_datetime(date)

    pr.result['content'] = tr[6].select('td')[1].text  # not rich text
    pr.result['links'] = [a.get('href') for a in tr[7].select('a')]

    td = tr[7].select('td')[1]
    attach_id_regex = re.compile('.*id=(\d+).*')
    pr.result['attachments'] = [
            {'name': a.text.strip(),
             'id': attach_id_regex.match(a.get('href')).group(1),
             'size': re.sub('[()]', '', span.text)}
            for a, span in zip(td.select('a'), td.select('span'))
        ]
    return pr


@need_login_check
def parse_homework_handin_list(body):
    pr = ParseResult(body)
    main = pr.soup.select_one('#main')
    if '目前尚無資料' in main.text:
        return pr

    # TODO: in not TA mode, some attrs will fail
    score_id_regex = re.compile('\d+score_(\d+)')
    for row in main.select('tr')[1:]:
        td = row.select('td')
        href = td[1].select_one('a').get('href')
        date = td[5].find('span').get('title')
        status = {
            'status_id': td[6].find('span').get('id'),
            'text': td[6].text
        }
        score_id = td[7].select('.hidden div a')[0].get('id')
        score = {
            'score_id': score_id_regex.match(score_id).group(1),
            'score_atag': td[7].select('.hidden div')[0].a
        }
        pr.result.append({
            'id': re.match('.*cid=(\d+).*', href).group(1),
            'title': td[1].text.strip(),
            'account_id': td[2].text,
            'authour': td[3].text,
            'status': status,
            'score': score,
            'date_string': date,
            'date': parse_datetime(date)
        })
    return pr


@need_login_check
def parse_homework_handin_detail(body):
    pr = ParseResult(body)
    main = pr.soup.select_one('#doc')
    if '目前尚無資料' in main.text:
        return pr

    attaches = main.select_one('.attach .block').select('div')
    for attach in attaches:
        a = attach.select('a')[1]
        hint = attach.select('.hint')[0]
        pr.result.append({
            'filename': a.get('title'),
            'id': a.get('href').split('=')[-1],
            'filesize': hint.text[1:-2]
        })

    return pr


@need_login_check
def parse_forum_list(body):
    pr = ParseResult(body)
    main = pr.soup.select_one('#main')
    if '目前尚無資料' in main.text:
        return pr

    for tr in main.select('tr')[1::2]:
        td = tr.select('td')
        pr.result.append({
            'id': td[0].text.strip(),
            'title': td[1].text.strip(),
            'count': td[2].find('span').text,
            'subtitle': td[3].text.strip()
        })

    page_info = pr.soup.select('.page span')
    if page_info:
        pages = len(page_info) - 2
        curr_page = pr.soup.select_one('.page .curr').text
        pr.extra = {
            'pages': pages if pages > 0 else 1,
            'curr_page': curr_page if pages > 0 else 1
        }

    return pr


@need_login_check
def parse_post_detail(json):
    pr = ParseResult()
    for item in json['posts']['items']:
        comment = {
            'name': item['name'],
            'date': item['date'],
            # 'note': html2text(item['note'])
            'note': item['note']
        }
        comment.update({
            'attachments': [(e['id'], e['srcName']) for e in item['attach']]
        }) if item['attach'] else None
        pr.result.append(comment)
    return pr


@need_login_check
def parse_material_list(body):
    pr = ParseResult(body)
    rows = pr.soup.select('tr')
    head = [e.text for e in rows[0].select('td')]
    for row in rows[1:]:
        item = {
            k: v.text.strip()
            for k, v in zip(head, row.select('td'))
        }
        item['id'] = row.select_one('a').get('href').split('=')[-1]
        pr.result.append(item)
    return pr


@need_login_check
def parse_material_detail(body):
    pr = ParseResult(body)
    title = pr.soup.select_one('.doc .title').text.strip()
    content = pr.soup.select_one('.doc .article').text.strip()

    attach = pr.soup.select_one('.attach .block')
    pr.extra = {'title': title, 'content': content}
    pr.result = [
        {
            'filename': a.get('title'),
            'id': a.get('href').split('=')[-1],
            'filesize': hint.text[1:-2]
        }
        for a, hint in zip(
            attach.select('a')[::2], attach.select('.hint'))
    ]
    return pr
