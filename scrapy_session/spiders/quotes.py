import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_session.pipelines.QuotesPipeline": 400,
            # "scrapy_session.pipelines.SaveToS3": 500,
            "scrapy_session.pipelines.QuotesByTagPipeline": 401,
        },
        "FEED_FORMAT": "json",
        "FEED_URI": "quotes.json"
    }

    # def parse(self, response):
    #     for element in response.xpath("//div[@class='quote']"):
    #         item = {
    #             'quote': element.xpath('span[@class="text"]/text()').get(),
    #             'author': element.xpath('span/small[@class="author"]/text()').get(),
    #             'tags': element.xpath('div[@class="tags"]/a[@class="tag"]/text()').getall()
    #         }
    #         print("ITEM: ",  item)
    #         yield item

    #     # Identifica el enlace a la siguiente página y sigue iterando
    #     next_page = response.xpath('//li[@class="next"]/a/@href').get()
    #     if next_page:
    #         yield response.follow(next_page, callback=self.parse)


    def parse(self, response):
        for element in response.css("div.quote"):
            item = {
                'quote': element.css("span.text::text").get(),
                'author': element.css("span small.author::text").get(),
                'tags': element.css("div.tags a.tag::text").getall()
            }
            print("ITEM: ", item)
            yield item

        # Identifica el enlace a la siguiente página y sigue iterando
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)