from html2text import html2text
from bs4 import BeautifulSoup


class ParseResult:

    def __init__(self, body=None):
        self.soup = BeautifulSoup(body, 'lxml') if body else None
        self.result = []
        self.extra = {}


def parse_course_list(body):
    pr = ParseResult(body)
    for item in pr.soup.select('.mnuItem')[:-2]:
        c, c_detail = item.find('a'), item.find('span')
        pr.result.append({
            'course_id': c.get('href').split('/')[-1],
            'course_name': c.text,
            'school_course_id': c_detail.text
        })
    return pr


def parse_homework_list(body):
    pr = ParseResult(body)
    for row in pr.soup.select('tr')[1:]:
        a = row.select_one('a')
        pr.result.append({
            'homework_id': a.get('href').split('=')[-1],
            'title': a.text.strip(),
            'deadline': row.select('td')[4].text.strip()
        })
    return pr


def parse_homework_detail(body):
    pr = ParseResult(body)
    pr.result = {'title': pr.soup.select_one('.curr').text}
    for i, row in enumerate(pr.soup.select('tr')[1:]):
        k, v = row.select('td')
        pr.result[k.text] = v.text
        if i == 5:
            pr.result['raw_description'] = v
        elif i == 6:
            pr.result[k.text] = [
                (a.text.strip(), a.get('href').split('=')[-1], span.text[1:-2])
                for a, span in zip(v.select('a'), v.select('span'))
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
            'note': html2text(item['note'])
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
