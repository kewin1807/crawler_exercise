import scrapy
from scrapy.loader import ItemLoader
from hotel_crawl.items import HotelCrawlItem
from hotel_crawl.constant import LIST_ID_CITY
from scrapy import Request
from scrapy.selector import Selector
import pdb
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from lxml import html
from time import sleep


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


html_getter = SeleniumHtmlGetter()


class HotelSpider(scrapy.Spider):

    # get 5 page hotel each city
    PAGES = 5
    EACH_HOTELS = 25
    name = "hotels"
    allowed_domains = ["booking.com"]
    start_urls = ["https://www.booking.com/index.vi.html"]

    # để ý id div đầu tiên
    selectors = {
        "hotel": "//*[@id='hotellist_inner']/div[2]",
        "hotel_name": "//*[@id='hotellist_inner']/div[2]/div[2]/div[1]/div[1]/div[1]/h3/a/span[1]",
        "address": "//*[@id='hotellist_inner']/div[2]/div[2]/div[1]/div[1]/div[2]/a",
        "quality_star": "//*[@id='hotellist_inner']/div[5]/div[2]/div[1]/div[1]/div[1]/span/span[1]/span/span",
        "rating": "//*[@id='hotellist_inner']/div[5]/div[2]/div[1]/div[2]/div/div/a[1]/div/div[1]",
        "number_people_rating": "//*[@id='hotellist_inner']/div[4]/div[2]/div[1]/div[2]/div/div/a[1]/div/div[2]/div[2]",
        "description": "//*[@id='hotellist_inner']/div[5]/div[2]/div[3]/div/div/div/div/div[1]/div/div[1]/span/strong",
        "price": "//*[@id='hotellist_inner']/div[1]/div[2]/div[3]/div/table/tbody/tr/td[2]/div[2]/strong/label",
        "distance": "//*[@id='hotellist_inner']/div[11]/div[2]/div[1]/div[1]/div[2]/span",
        "image": "//*[@id='hotellist_inner']/div[10]/div[1]/a/img"
    }

    def parse(self, response, **kwargs):
        objectLink = {}
        for key in LIST_ID_CITY:
            objectLink[key] = []
            for page in range(self.PAGES):
                offset = self.EACH_HOTELS * page
                link = "https://www.booking.com/searchresults.vi.html?dest_id={}&dest_type=region&order=popularity&offset={}&checkin_year=2020&checkin_month=12&checkin_monthday=30&checkout_year=2020&checkout_month=12&checkout_monthday=31&group_adults=2&group_children=0&no_rooms=1&from_sf=1".format(
                    key, offset)
                objectLink[key].append(link)
        for key in LIST_ID_CITY:
            for link in objectLink[key]:

                html_tree = html_getter.get_html(link)
                hotel_items = self.parse_hotel(html_tree, city_id=key)
                if hotel_items and len(hotel_items) > 0:
                    for hotel in hotel_items:
                        print(hotel.load_item())
                        yield hotel.load_item()
                # yield Request(url=link, callback=self.parse_hotel, meta={'city_id': key})

    def parse_hotel(self, html_tree, city_id):
        hotel_items = []
        scrapy_selector = Selector(text=html_tree)
        hotels = scrapy_selector.xpath(
            "//*[@id='hotellist_inner']/div[@data-score]")
        if hotels is not None and len(hotels) > 0:
            for index, hotel in enumerate(hotels):
                hotel_selector_text = hotel.get()
                hotel_selector = Selector(text=hotel_selector_text)
                loader = ItemLoader(item=HotelCrawlItem(),
                                    selector=hotel_selector)
                loader.add_css("hotel_name", ".sr-hotel__name::text")
                loader.add_xpath("hotel_id", "//div[1]/@id")
                loader.add_css("address", ".bui-link::text")
                loader.add_css("image", "img::attr(src)")
                loader.add_value("city_id", city_id)

                # get rating score
                rating_path = hotel_selector.xpath(
                    "//div[2]/div[1]/div[2]/div/div/a[1]/div/div[1]/text()")
                if len(rating_path) > 0:

                    loader.add_xpath(
                        "rating", "//div[2]/div[1]/div[2]/div/div/a[1]/div/div[1]/text()")
                    # get number_people_rating
                    loader.add_xpath(
                        "number_people_rating", "//div[2]/div[1]/div[2]/div/div/a[1]/div/div[2]/div[2]/text()")
                else:
                    loader.add_value("rating", ["0.0"])
                    loader.add_value("number_people_rating", ["0"])
                # get price
                loader.add_xpath(
                    "price", "//div[@class='bui-price-display__value prco-inline-block-maker-helper ']/text()")
                # get distance
                loader.add_xpath(
                    "distance", "//div[2]/div[1]/div[1]/div[2]/a/@data-coords")
                # get link
                loader.add_xpath(
                    "link", "//div[2]/div[1]/div[1]/div[2]/a/@href")
                # get description
                loader.add_css("description", ".room_link span strong::text")
                # get quality_star
                rating_stars = hotel_selector.xpath(
                    "//span[@class='bui-rating bui-rating--smaller']/@aria-label")
                if len(rating_stars) > 0:
                    loader.add_xpath(
                        "quality_star", "//span[@class='bui-rating bui-rating--smaller']/@aria-label")
                else:
                    loader.add_value("quality_star", ["0"])
                hotel_items.append(loader)
        return hotel_items
