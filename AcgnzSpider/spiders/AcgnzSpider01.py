# -*- coding: utf-8 -*-

import scrapy
import logging

from scrapy.utils.project import get_project_settings
from time import sleep

from AcgnzSpider.items import AcgnzItem


class AcgnzSpider(scrapy.Spider):
    name = 'acgnz.cc'
    start_urls = ['http://www.acgnz.cc/sign']
    allowed_domains = ['acgnz.cc']

    def parse(self, response):
        settings = get_project_settings()
        yield scrapy.FormRequest.from_response(
            response,
            method='POST',
            # headers={'Content-Type': 'multipart/form-data'},
            url='http://www.acgnz.cc/wp-admin/admin-ajax.php?action=theme_custom_sign',
            formdata={
                'user[email]': self.settings.get('LOGIN_CREDENTIALS_EMAIL'),
                'user[pwd]': self.settings.get('LOGIN_CREDENTIALS_PWD'),
                'user[remember]': '1',
                'type': 'login',
                'theme-nonce': '85dd62e1f6'
            },
            callback=self.parse_follow_seq
        )

    def parse_follow_seq(self, response):
        if 'success' not in response.body:
            raise CloseSpider('login failed')
        logging.log(logging.DEBUG, 'login successful, sleeping for 5 seconds')
        sleep(5)

        for i in range(9000):
            yield scrapy.Request(
                'http://www.acgnz.cc/{index}'.format(index=i),
                meta={'dont_redirect': True,
                      'handle_httpstatus_list': [302]},
                callback=self.parse_page)

    def parse_page(self, response):
        if response.status == 302:
            pass
        else:
            item = AcgnzItem()
            item['url'] = response.url
            item['title'] = (response.selector.xpath('//div[@class="entry-content content-reset"]').xpath(
                './/a/@title').extract() + response.selector.xpath('//article[@id]/h2/text()').extract())[0]
            item['image_urls'] = response.selector.xpath(
                '//div[@class="entry-content content-reset"]').xpath('.//img/@src').extract()
            if response.selector.xpath('//div[@class="entry-circle"]/a[@class="meta meta-post-storage"]/@href'):
                download_page_href = response.selector.xpath(
                    '//div[@class="entry-circle"]/a[@class="meta meta-post-storage"]/@href')[0].extract()
                yield scrapy.Request(download_page_href, meta={'item': item}, callback=self.parse_download_page)
            else:
                item['download_link'] = ''
                item['download_code'] = ''
                item['unarchive_password'] = ''
                yield item

    def parse_download_page(self, response):
        item = response.meta['item']

        item['download_link'] = response.selector.xpath('//div[@class="post-download"]').xpath(
            './/a[@class="btn btn-lg btn-success btn-block"]/@href')[-1].extract()

        if response.selector.xpath(
                '//div[@class="post-download"]').xpath('.//input[@id="theme_custom_storage-0-download-pwd"]/@value'):
            item['download_code'] = response.selector.xpath(
                '//div[@class="post-download"]').xpath('.//input[@id="theme_custom_storage-0-download-pwd"]/@value')[-1].extract()

        if response.selector.xpath(
                '//div[@class="post-download"]').xpath('.//input[@id="theme_custom_storage-0-extract-pwd"]/@value'):
            item['unarchive_password'] = response.selector.xpath(
                '//div[@class="post-download"]').xpath('.//input[@id="theme_custom_storage-0-extract-pwd"]/@value')[-1].extract()

        yield item
