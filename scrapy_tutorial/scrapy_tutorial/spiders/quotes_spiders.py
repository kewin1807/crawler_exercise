import scrapy


class QuotesSpider(scrapy.Spider):
    # name of spider
    name = "quotes"

    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):

        # run command line scrapy shell `&{url}` to analyze response
        self.logger.info("hello this is my first crawl")
        quotes = response.css('div.quote')
        for quote in quotes:
            yield {
                # get value in element with ".class_css_name::text"
                "text": quote.css(".text::text").get(),
                "author": quote.css(".author::text").get(),
                "tags": quote.css(".tag::text").get(),
            }

            author_url = quote.css('.author + a::attr(href)').get()
            self.logger.info('get author page url')
            # go to the author page
            yield response.follow(author_url, callback=self.parse_author)

        # find element html to click next page
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)

            # sends a new request to get the next page and use a callback function to call the same parse function
            yield scrapy.Request(next_page, callback=self.parse)
        pass

    def parse_author(self, response):
        yield {
            'author_name': response.css('.author-title::text').get(),
            'author_birthday': response.css('.author-born-date::text').get(),
            'author_bornlocation': response.css('.author-born-location::text').get(),
            'author_bio': response.css('.author-description::text').get(),
        }
