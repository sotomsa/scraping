import scrapy
from ..items import ScrapingItem

class ColombianoSpider(scrapy.Spider):
    name = 'elcolombiano'
    start_urls = ["https://www.elcolombiano.com/antioquia#._531700976_p:1;"]

    def parse(self, response):
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
            yield items

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