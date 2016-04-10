from bs4 import BeautifulSoup


def parse_course_list(body):
    soup = BeautifulSoup(body, 'lxml')
    result = []
    for item in soup.select('.mnuItem'):
        try:
            c, c_detail = item.find('a'), item.find('span')
            result.append({
                'ilms_id': c.get('href').split('/')[-1],
                'course_name': c.text,
                'course_id': c_detail.text
            })
        except:
            pass
    return result
