import scrapy
from scrapy.http import Response, FormRequest, Request
from scrapy.utils.response import open_in_browser
from ..items import ScrapingItem
from selenium import webdriver

class ColombianoSpider(scrapy.Spider):
    name = 'elcolombiano'
    #start_urls = ["https://www.elcolombiano.com/antioquia#._531700976_p:1;"]
    start_urls = ["https://www.elcolombiano.com/inicio-sesion"]

    def get_cookies(self):
        driver = webdriver.Firefox()
        driver.implicitly_wait(30)
        base_url = "https://www.elcolombiano.com/inicio-sesion"
        driver.get(base_url)
        driver.find_element_by_name("userInput").clear()
        driver.find_element_by_name("userInput").send_keys("sotomsa@gmail.com")
        driver.find_element_by_name("inputPassword").clear()
        driver.find_element_by_name("inputPassword").send_keys("71265msa")
        driver.find_element_by_name("btnLogin").click()
        cookies = driver.get_cookies()
        driver.close()
        return cookies

    def parse(self, response, my_cookies=get_cookies):
        return [Request(response, 
                       url="https://www.elcolombiano.com/antioquia#._531700976_p:1;", 
                       callback=self.parse_other,
                       cookies=my_cookies)]

    def parse_other(self, response):
        open_in_browser(response)
        articles = response.css(".paged  article")
        
        for article in articles:            
            title = article.css("span.priority-content::text").extract_first()
            category = article.css("div.categoria-noticia a::text").extract_first()
            date_pre = article.css("div.categoria-noticia::text").extract()[-1]
            url = article.css("div.left").extract()
            idx_start = date_pre.find('|') + 2
            idx_end = date_pre.find('\n') - 1
            date = date_pre[idx_start: idx_end]
            short_summary = article.css("div.right p::text")[1].extract()
            url = "https://www.elcolombiano.com" + article.css("div.left a::attr(href)").extract_first()
            
            items = dict()
            items['title'] = title
            items['category'] = category
            items['date'] = date
            items['short_summary'] = short_summary
            items['url'] = url
            yield scrapy.Request(url, callback=self.parse_news, cb_kwargs=items)
            #yield items

    def parse_news(self, response, title, category, date, short_summary, url):

        items = ScrapingItem()
        items['title'] = title
        items['gnal_category'] = 'antioquia'
        items['category'] = category
        items['date'] = date
        items['short_summary'] = short_summary
        items['url'] = url
        items['img_description'] = response.css(".caption-img::text").extract_first()
        items['tags'] = response.css("div.block-tags")[0].css("span::text").extract()
        items['text'] = response.css(".block-text")[0].css('p::text').extract()
        return items