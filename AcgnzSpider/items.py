# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AcgnzItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    image_urls = scrapy.Field()
    download_link = scrapy.Field()
    download_code = scrapy.Field()
    unarchive_password = scrapy.Field()
    pass
