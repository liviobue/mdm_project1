from datetime import datetime
import scrapy
from ..items import YahooscrapingItem

class MostactiveSpider(scrapy.Spider):
    name = 'scrape_tesla'
    
    def start_requests(self):
        urls = ['https://finance.yahoo.com/quote/TSLA?p=TSLA']  # Microsoft Stocks start URL
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        #Declare the item objects
        items = YahooscrapingItem()
        
        # Save the current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Save the extracted data in the item objects
        items['stock_name'] = response.xpath('//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1').css('::text').extract()
        items['intraday_price'] = response.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[1]').css('::text').extract()
        items['price_change'] = response.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[3]/span').css('::text').extract()
        items['volume'] = response.xpath('//*[@id="quote-summary"]/div[1]/table/tbody/tr[7]/td[2]/fin-streamer').css('::text').extract()
        items['current_timestamp'] = [current_date]

        yield items
