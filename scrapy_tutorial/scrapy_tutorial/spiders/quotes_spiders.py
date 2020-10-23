import scrapy
from scrapy.loader import ItemLoader
from scrapy_tutorial.items import QuoteItem
# ItemLoader can process raw_data which get from the css (define in Item)


class QuotesSpider(scrapy.Spider):
    # name of spider
    name = "quotes"
    allowed_domains = ["toscrape.com"]
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):

        # run command line scrapy shell `&{url}` to analyze response
        self.logger.info("hello this is my first crawl")
        quotes = response.css('div.quote')
        for quote in quotes:
            # yield {
            #     # get value in element with ".class_css_name::text"
            #     "text": quote.css(".text::text").get(),
            #     "author": quote.css(".author::text").get(),
            #     "tags": quote.css(".tag::text").get(),
            # }

            loader = ItemLoader(item=QuoteItem(), selector=quote)
            # pay attention to the dot .// to use relative xpath
            # loader.add_xpath('quote_content', ".//span[@class='text']/text()")
            loader.add_css('quote_content', '.text::text')
            # loader.add_xpath('author', './/small//text()')
            loader.add_css('tags', '.tag::text')
            quote_item = loader.load_item()

            author_url = quote.css('.author + a::attr(href)').get()
            self.logger.info('get author page url')

            # pass metadata quote_item after crawl quote_content then crawl author by other link
            yield response.follow(author_url, callback=self.parse_author, meta={'quote_item': quote_item})

        # find element html to click next page
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)

            # sends a new request to get the next page and use a callback function to call the same parse function
            yield scrapy.Request(next_page, callback=self.parse)
        pass

    def parse_author(self, response):
        quote_item = response.meta['quote_item']
        loader = ItemLoader(item=quote_item, response=response)
        loader.add_css('author_name', '.author-title::text')
        loader.add_css('author_birthday', '.author-born-date::text')
        loader.add_css('author_bornlocation', '.author-born-location::text')
        loader.add_css('author_bio', '.author-description::text')
        yield loader.load_item()
        # yield {
        #     'author_name': response.css('.author-title::text').get(),
        #     'author_birthday': response.css('.author-born-date::text').get(),
        #     'author_bornlocation': response.css('.author-born-location::text').get(),
        #     'author_bio': response.css('.author-description::text').get(),
        # }
