from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class HtmlGetter:
    def get_html(self, url):
        pass


class HtmlParseGetter(HtmlGetter):
    def __init__(self, subject):
        self.subject = subject

    def get_html(self, url):
        html_source = self.subject.get_html(url)
        html_element = html.fromstring(html_source)
        return html_element


class SeleniumHtmlGetter(HtmlGetter):
    def __init__(self, scroll_to_bottom=False):
        self.scroll_to_bottom = scroll_to_bottom

    def get_html(self, url):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        PROXY = "us-wa.proxymesh.com:31280"
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        browser = webdriver.Chrome(
            "chromedriver/chromedriver", options=chrome_options)
        browser.maximize_window()
        browser.get(url)
        if self.scroll_to_bottom:
            last = None
            for v in range(500):
                for k in range(5):
                    browser.find_element_by_xpath(
                        '//html').send_keys(Keys.DOWN)
                if last is not None and last == browser.execute_script('return window.pageYOffset;'):
                    break
                last = browser.execute_script('return window.pageYOffset;')
        html_source = browser.page_source
        browser.quit()
        return html_source


if __name__ == '__main__':
    url = 'https://tiki.vn/deal-hot?src=header_label&_lc=Vk4wMzQwMjAwMDM%253D&tab=now&page=1'
    html_getter = HtmlParseGetter(SeleniumHtmlGetter())
    html_tree = html_getter.get_html(url)
    for v in html_tree.xpath("//*[@data-view-id='product_item']"):
        objectResult = {}
        objectResult["title"] = v.xpath("./p[@class='title']/text()")[0]
        objectResult["price_sale"] = v.xpath("./p[@class='price']/text()")[0]
        objectResult["img"] = v.xpath(
            "./div[@class='Item__Picture-m1oy8w-1 evEsoa']//img/@src")[0]
        objectResult["original"] = v.xpath(
            "./p[@class='price']//span[@class='original deal']/text()")[0]
        print(objectResult)
