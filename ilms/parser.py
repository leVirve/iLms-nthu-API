import re
from datetime import datetime

# from html2text import html2text
from bs4 import BeautifulSoup


class ParseResult:

    def __init__(self, body=None):
        self.soup = BeautifulSoup(body, 'lxml') if body else None
        self.result = []
        self.extra = {}

pad = ['', ' ', '  ', '   ', ]


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


def parse_profile(body):
    pr = ParseResult(body)
    name = pr.soup.select_one('#fmName').get('value')
    email = pr.soup.select_one('#fmEmail').get('value')
    pr.result = {'name': name, 'email': email}
    return pr


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
            'course_id': fix_course_id_padding(course_id)
        })
    return pr


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


def parse_forum_list(body):
    pr = ParseResult(body)
    for row in pr.soup.select('tr')[1::2]:
        item = row.select('td')
        pr.result.append((
            item[0].text.strip(),
            item[1].text.strip()
        ))
    pages = len(pr.soup.select('.page span')) - 2
    curr_page = pr.soup.select_one('.page .curr').text
    pr.extra = {
        'pages': pages if pages > 0 else 1,
        'curr_page': curr_page if pages > 0 else 1
    }
    return pr


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


def parse_doc_list(body):
    pr = ParseResult(body)
    rows = pr.soup.select('tr')
    head = [e.text for e in rows[0].select('td')]
    for row in rows[1:]:
        item = {
            k: v.text.strip()
            for k, v in zip(head, row.select('td'))
        }
        item['material_id'] = row.select_one('a').get('href').split('=')[-1]
        pr.result.append(item)
    return pr


def parse_doc_detail(body):
    pr = ParseResult(body)
    title = pr.soup.select_one('.doc .title').text.strip()
    content = pr.soup.select_one('.doc .article').text.strip()
    pr.extra = {'title': title, 'content': content}
    pr.result = [
        {
            'filename': a.get('title'),
            'attachment_id': a.get('href').split('=')[-1],
            'filesize': hint.text[1:-2]
        }
        for a, hint in zip(
            pr.soup.select('.attach a')[::2], pr.soup.select('.attach  .hint'))
    ]
    return pr
