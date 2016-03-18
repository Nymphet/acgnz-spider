# acgnz-spider
Crawler for wordpress sites with acgnz theme, e.g. acgnz.cc, a.acgluna.com

    scrapy crawl acgnz.cc

if you'd like to save the results, add `-o` parameter

    scrapy crawl acgnz.cc -o some_json_file_name.json

Fill in your login credentials in `settings.py` before you start to crawl, or just remove the login part in the code if you don't need to login.

By default the crawler will only extract post url, basic info, image addresses and download links. if you'd like to download the images also, add the following lines to `settings.py`

    ITEM_PIPELINES = {'scrapy.pipelines.images.ImagesPipeline': 1} 
    IMAGES_STORE = '/path to save'
