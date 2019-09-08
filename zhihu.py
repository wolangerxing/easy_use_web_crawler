import os
import platform

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

import secret


def add_chrome_webdriver():
    print(platform.system())
    working_path = os.getcwd()
    library = 'library'
    path = os.path.join(working_path, library)
    os.environ['PATH'] += '{}{}{}'.format(os.pathsep, path, os.pathsep)
    print(os.environ['PATH'])


def add_cookie(browser):
    browser.delete_all_cookies()
    print('before', browser.get_cookies())
    for part in secret.cookie.split(';'):
        kv = part.split(':', 1)
        d = dict(
            name=kv[0],
            value=kv[1],
            path='/',
            domain='.zhihu.com',
            secure=True
        )
        print('cookie', d)
        browser.add_cookie(d)
    print('after', browser.get_cookies())


def scroll_to_end(browser):
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')


def start_crawler(browser):
    # chrome 有 bug https://bugs.chromium.org/p/chromium/issues/detail?id=617931
    # 不能 --user-data-dir 和 --headless 一起用
    # 改回用 cookie

    url = "https://www.zhihu.com/follow"
    # 先访问一个 url，才能设置这个 url 对应的 cookie
    browser.get("https://www.zhihu.com/404")
    add_cookie(browser)
    browser.get(url)
    while True:
        print('拿到更多数据')
        cards = browser.find_elements_by_css_selector('.Card.TopstoryItem')
        for card in cards:
            try:
                source = card.find_element_by_css_selector('.FeedSource-firstline')
            except NoSuchElementException:
                pass
            else:
                if '1 天前' in source.text:
                    print('拿到了最近1天动态')
                    titles = browser.find_elements_by_css_selector('.ContentItem-title')
                    for title in titles:
                        print(title.text)
                    return
        # 当这次鼠标滚动找不到数据的时候，执行下一次滚动
        scroll_to_end(browser)


def main():
    # cookie 要去掉 _xsrf _zap tgw_l7_route 这三个
    add_chrome_webdriver()

    o = Options()
    # o.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=o)
    try:
        start_crawler(browser)
    finally:
        browser.quit()


if __name__ == '__main__':
    main()
