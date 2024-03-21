from datetime import datetime
import scrapy
from ..items import YahooscrapingItem

class MostactiveSpider(scrapy.Spider):
    name = 'scrape_mostactive'
    def start_requests(self):
        urls = ['https://finance.yahoo.com/most-active/']  # Most active Stocks start URL
        for url in urls:
            yield scrapy.Request(url=url, callback=self.get_stocks)

    def get_stocks(self, response):
        # Get all the stock symbols
        stocks = response.xpath('//*[@id="scr-res-table"]/div[1]/table/tbody//tr/td[1]/a').css('::text').extract()
        for stock in stocks:
            # Follow the link to the stock details page.
            yield scrapy.Request(url=f'https://finance.yahoo.com/quote/{stock}?p={stock}', callback=self.parse)


    def parse(self, response):
        #Declare the item objects
        items = YahooscrapingItem()
        current_date = datetime.now().strftime("%Y-%m-%d")
        #Save the extracted data in the item objects
        items['stock_name'] = response.xpath('//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1').css('::text').extract()
        items['intraday_price'] = response.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[1]').css('::text').extract()
        items['price_change'] = response.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[3]/span').css('::text').extract()
        items['volume'] = response.xpath('//*[@id="quote-summary"]/div[1]/table/tbody/tr[7]/td[2]/fin-streamer').css('::text').extract()
        items['current_timestamp'] = [current_date]

        yield items