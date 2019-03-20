# -*- coding: utf-8 -*-
import scrapy
from ..items import SpiderbookItem

class BookspiderSpider(scrapy.Spider):
    name = 'bookspider'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']


    # 书籍列表页面的解析
    # 完成两个任务，1是提取书籍页面的链接，构造Request对象并提交
    # 2是提取下一页书籍列表的链接，构造Request对象并提交
    def parse(self, response):
        le = scrapy.linkextractors.LinkExtractor(restrict_css='article.product_pod h3')
        #le = scrapy.linkextractors.LinkExtractor(restrict_xpaths='//product_pod@href')
        for link in le.extract_links(response):
            yield scrapy.Request(link.url,callback=self.parse_book)

        le = scrapy.linkextractors.LinkExtractor(restrict_css='ul.pager li.next')
        links = le.extract_links(response)
        if links:
            next_url = links[0].url
            yield scrapy.Request(next_url,callback=self.parse)

    # 书籍页面的解析
    def parse_book(self,response):
        book = SpiderbookItem()
        
        '''采用css解析页面'''
        sel = response.css('#content_inner > article > div.row > div.col-sm-6.product_main')
        book['name'] = sel.css('h1::text').extract_first()
        book['price'] = sel.css('p.price_color::text').extract_first()
        book['review_rating'] = sel.css('p.star-rating').re_first('star-rating ([A-Za-z]+)')
        sel = response.css('table.table.table-striped')
        book['upc'] = sel.css('tr:nth-child(1) > td::text').extract_first()
        book['stock'] = sel.css('tr:nth-last-child(2) > td::text').re_first(r'\d+')
        book['review_num'] = sel.css('tr:nth-last-child(1) > td::text').extract_first()

        
        '''采用xpath解析页面
        book['name'] = response.xpath("//*[@id='content_inner']//article/div[1]/div[2]/h1/text()").extract_first()
        print(book['name'] )
        book['price'] = response.xpath("//*[@id='content_inner']//article/div[1]/div[2]/p[1]/text()").extract_first() 
        print(book['price'] )
        book['review_rating'] = response.xpath("//p[contains(@class,'star-rating')]/@class").re_first('star-rating ([A-Za-z]+)') 
        print(book['review_rating'] )
        book['upc'] = response.xpath('//table[@class="table table-striped"]/tr[1]/td/text()').extract_first()
        print(book['upc'] )
        book['stock'] = response.xpath('//table[@class="table table-striped"]/tr[last()-1]/td/text()').re_first(r'\d+')
        print(book['stock'] )
        book['review_num'] = response.xpath('//table[@class="table table-striped"]/tr[last()]/td/text()').extract_first()
        print(book['review_num'] )
        '''
        yield book

        #scrapy crawl bookspider -o book_xpath.csv --nolog