import scrapy
from lxml import html
from itertools import zip_longest
from scrapy import Request

class TucarroSpider(scrapy.Spider):
    name = "tucarro"
    allowed_domains = ["carros.tucarro.com.co"]
    start_urls = [
        "https://carros.tucarro.com.co/bogota-dc/_PriceRange_0-35000000_NoIndex_True"
    ]
    
    custom_settings = {
        "COOKIES_ENABLED": True,
        "COOKIES": {
            '_d2id': '07deaa95-db21-49db-89df-f3382b9d0110',
            'ftid': 'dKwFRb8rCrfeL54SAWGEwap35mtCpuNB-1708372566693',
            'orguseridp': '101223788',
            'orgnickp': 'BAYONAC2012',
            'orguserid': 'Z0d00dZZHh77',
            'ssid': 'ghy-021915-0vBjlJSiV51AR3ug5mmSosDLLX1Dyf-__-101223788-__-1803067007261--RRR_0-RRR_0',
            'cookiesPreferencesLogged': '%7B%22userId%22%3A101223788%2C%22categories%22%3A%7B%7D%7D',
            'cookiesPreferencesLoggedFallback': '%7B%22userId%22%3A101223788%2C%22categories%22%3A%7B%7D%7D',
            '_csrf': 'h-c9_QQ-TABXolr69zHdUhUL',
            'c_ui-navigation': '5.19.7',
            '_mldataSessionId': '6497d7ae-e575-4255-9406-b8efc1a9934a',
            '_tc_ga': 'GA1.3.1982315183.1710195486',
            '_tc_ga_gid': 'GA1.3.1256973879.1710195486',
            '_tc_ci': '1982315183.1710195486',
            '_tc_dc': '1',
            'FCNEC': '%5B%5B%22AKsRol-R79zLBtadJ42E6V9BEiuzasvX1Crliw82HlwV8xy5hZXvSBMyHneYI_uDqiN1RzrteTqSIdrcxmhimdtv5JQ48c8E9GwqZPMaD9VEcVj4LVTuFW7wuNOd17DVQ6fGu4x3jPY-W14XxvTySUlT22NioEnrwA%3D%3D%22%5D%5D',
            '_tc_cbanner_mco': '1',
        },
        "DEFAULT_REQUEST_HEADERS": {
            'authority': 'carros.tucarro.com.co',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-CO,en;q=0.9,es-CO;q=0.8,es;q=0.7,en-US;q=0.6',
            'device-memory': '8',
            'downlink': '10',
            'dpr': '2',
            'ect': '4g',
            'priority': 'u=0, i',
            'referer': 'https://carros.tucarro.com.co/bogota-dc/',
            'rtt': '50',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'viewport-width': '1792',
        },
        "FEED_FORMAT": "json",
        "FEED_URI": "tucarro.json"
    }

    def parse(self, response):
        # Extraer enlaces a cada anuncio de automóvil
        car_links = response.xpath('//li[@class="ui-search-layout__item"]//a/@href').extract()
        for link in car_links:
            yield response.follow(link, callback=self.parse_car_details)

        # Obtener el enlace de la siguiente página
        next_page = response.xpath('//li[@class="andes-pagination__button andes-pagination__button--next"]//@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_car_details(self, response):
        car = {}
        
        # Extraer datos principales
        car["url"] = response.url
        car["title"] = response.xpath('//h1[@class="ui-pdp-title"]/text()').get(default="")
        
        subtitle = response.xpath('//div[@class="ui-pdp-header__subtitle"]/span/text()').get(default="")
        car["model"] = subtitle.split(" | ")[0] if " | " in subtitle else ""
        car["kms"] = subtitle.split(" | ")[1].split(" · ")[0] if " | " in subtitle and " · " in subtitle else ""
        car["price"] = response.xpath('//span[@data-testid="price-part"]//span[@class="andes-money-amount__fraction"]/text()').get(default="")

        # Extraer especificaciones
        details = response.xpath('//section[@id="highlighted_specs_attrs"]//div[@class="ui-vpp-highlighted-specs__key-value"]//p//text()').extract()
        details = [detail.strip() for detail in details if detail.strip()]
        
        keys = details[::2]
        values = details[1::2]
        dict_details = dict(zip_longest(keys, values))
        car.update(dict_details)
        yield car
