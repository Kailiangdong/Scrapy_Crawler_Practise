import scrapy
from tumjob.items import TumjobItem
class tumjobspider(scrapy.Spider):
    name = "tumjob"
    allowed_domains = ['db.alumni.tum.de']
    #start_urls = ['https://*****.de/jobs/search?utf8=%E2%9C%93&search%5Bq%5D=werkstudent', 'https://db.alumni.tum.de/jobs/search?utf8=%E2%9C%93&search%5Bq%5D=working+student']

    def start_requests(self):
        #scrapy crawl tumjob -o items.json -a keyword=werkstudent
        url = 'https://****.tum.de/jobs/search?utf8=%E2%9C%93&search%5Bq%5D='
        keyword = getattr(self,'keyword',None)
        if keyword is not None:
            url = url + keyword
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        for sel in response.xpath('//div/section/ul[@id="jobs"]/li'):
            item = TumjobItem()
            trans_table = {ord(c): None for c in u'\r\n\t'}
            item['name'] = sel.css('strong::text').get()
            item['description']= ' '.join(s.translate(trans_table) for s in sel.css('a::text').getall())
            item['time'] = sel.css('time::text').get()
            item['id'] = sel.css('a::attr(href)').get()[-6:]
            yield item

        next_page = response.xpath('//a[@class="next_page"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
