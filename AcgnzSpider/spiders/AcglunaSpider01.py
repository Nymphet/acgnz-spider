# -*- coding: utf-8 -*-

import scrapy
import logging

from scrapy.utils.project import get_project_settings
from time import sleep

from AcgnzSpider.items import AcglunaItem


class AcgnzSpider(scrapy.Spider):
    name = 'a.acgluna.com'
    start_urls = ['http://a.acgluna.com/sign']
    allowed_domains = ['acgluna.com']

    def parse(self, response):
        settings = get_project_settings()
        yield scrapy.FormRequest.from_response(
            response,
            method='POST',
            # headers={'Content-Type': 'multipart/form-data'},
            url='http://a.acgluna.com/wp-admin/admin-ajax.php?action=theme_custom_sign',
            formdata={
                'user[email]': self.settings.get('LOGIN_CREDENTIALS_EMAIL'),
                'user[pwd]': self.settings.get('LOGIN_CREDENTIALS_PWD'),
                'user[remember]': '1',
                'type': 'login',
                'theme-nonce': 'b91d7f5b54'
            },
            callback=self.parse_follow_seq
        )

    def parse_follow_seq(self, response):
        if 'success' not in response.body:
            raise CloseSpider('login failed')
        logging.log(logging.DEBUG, 'login successful, sleeping for 5 seconds')
        sleep(5)

        for i in range(20000):
            yield scrapy.Request(
                'http://a.acgluna.com/archives/{index}'.format(index=i),
                meta={'dont_redirect': True,
                      'handle_httpstatus_list': [302]},
                callback=self.parse_page)

    def parse_page(self, response):
        if response.status == 302:
            pass
        else:
            item = AcglunaItem()
            item['url'] = response.url
            item['title'] = (response.selector.xpath('//div[@class="entry-content content-reset"]').xpath(
                './/a/@title').extract() + response.selector.xpath('//article[@id]/h2/text()').extract())[0]
            item['image_urls'] = response.selector.xpath(
                '//div[@class="entry-content content-reset"]').xpath('.//img/@src').extract()
            item['post_content'] = response.selector.xpath('//div[@class="entry-body"]')[0].extract()

            if response.selector.xpath('//a/@href[contains(., "pan.baidu.com")]'):
                item['possible_download_links__obsolete_style'] = response.selector.xpath('//a/@href[contains(., "pan.baidu.com")]').extract()
                item['possible_download_codes__obsolete_style'] = []
                for text in response.xpath('//text()').extract():
                    if u'\u5bc6\u7801' in text:
                        item['possible_download_codes__obsolete_style'].append(text)
            else:
                item['possible_download_links__obsolete_style'] = []
                item['possible_download_codes__obsolete_style'] = []

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
        else:
            item['download_code'] = ''

        if response.selector.xpath(
                '//div[@class="post-download"]').xpath('.//input[@id="theme_custom_storage-0-extract-pwd"]/@value'):
            item['unarchive_password'] = response.selector.xpath(
                '//div[@class="post-download"]').xpath('.//input[@id="theme_custom_storage-0-extract-pwd"]/@value')[-1].extract()
        else:
            item['unarchive_password'] = ''

        yield item
