
This is an introduction and tutorial of Scrapy
# Introduction
Scrapy is a framework of python to crawl infomation from website quickly and better.
It encapsulate a lot. So you only have to code in repository spider, item.py and pipeitem.py.
For detail, you can see the document of Scrapy   https://docs.scrapy.org/en/latest/

# Objective
Our target is to crawl the job information from job portal https://*****/jobs(Because of TOS, I hidden the website)
When user run the program, they can input the keyword and cral all information like name, description and time of jobs related with keyword.

**Let's start**
# Preparation
First you should install Scrapy on you pc
```python
pip install scrapy
```
For me , I have Anaconda on my computer, so,
```python
conda install -c conda-forge/label/cf201901 scrapy
```
# Create a project
type in terminal
```python
scrapy startproject tumjob
```
It will create a repository for you ,like this
```python
tumjob/
    scrapy.cfg
    tumjob/
        __init__.py
        items.py
        pipelines.py
        settings.py
        spiders/
            __init__.py
            ...

```
Let me introduce the file briefly to you.
## items.py 
Its function is for output format. Once you give the name you want, you will have output format.Like this.
```python
import scrapy


class TumjobItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    description = scrapy.Field()
    time = scrapy.Field()
    id = scrapy.Field()
```
And you will get final this json files
```json
{"name": "Werkstudent für Bauprojektmanagement", "description": " Werkstudent in München at bavaria PS GmbH  ", "time": "2019-06-16", "id": "180053"}
```
## pipelines.py
Typical uses of item pipelines are:
cleansing HTML data
validating scraped data (checking that the items contain certain fields)
checking for duplicates (and dropping them)
storing the scraped item in a database
For this project, it will remove duplicates item by id (That is why we should add id in items and also crawl identify id of every item.
```python
class TumjobPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['id'])
            return item
```

## setting.py
like its name, it controls all setting of this project. We should add this to activate pipeitems.
```python
ITEM_PIPELINES = {
   'tumjob.pipelines.TumjobPipeline': 300,
}
```
OK. Then the main part, spider. In the spider repository, we should create our own spider which includes the logic and process of our crawler.

# make you spider
Firstly , I will give you general mind of the code. Then pay attention to xpath and css selector. If you have mind of crawler , you should now how to pick selector is main part of crawler.

```python
import scrapy
from tumjob.items import TumjobItem
class tumjobspider(scrapy.Spider):
    name = "tumjob"   #This is name of spider, you will need this name when you run the spider,like "scrapy crawl tumjob -o item.json
    allowed_domains = ['*****.de']  # allowed domain, all website to crawl should be in this domain
    #start_urls = ['https://*****.de/jobs/search?utf8=%E2%9C%93&search%5Bq%5D=werkstudent', 'https://*****.de/jobs/search?utf8=%E2%9C%93&search%5Bq%5D=working+student']
	# For simple coding, you can use starturl, it will crawl this url automatically, but if you want to like me to insert some search keyword as argument to crawl , You should use start_requests
    def start_requests(self):
        #scrapy crawl tumjob -o items.json -a keyword=werkstudent
        url = 'https://****.tum.de/jobs/search?utf8=%E2%9C%93&search%5Bq%5D='
        keyword = getattr(self,'keyword',None)
        # get attribute from shell , "scrapy crawl tumjob -o items.json -a           keywords=werkstudent"
        if keyword is not None:
            url = url + keyword
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
    # parse is the callback function of the crawl, after make the request, it will run parse
        for sel in response.xpath('//div/section/ul[@id="jobs"]/li'):
            item = TumjobItem()  # Create the item
            trans_table = {ord(c): None for c in u'\r\n\t'}  # To remove \r\n\t in the output
            item['name'] = sel.css('strong::text').get()
            item['description']= ' '.join(s.translate(trans_table) for s in sel.css('a::text').getall())
            item['time'] = sel.css('time::text').get()
            item['id'] = sel.css('a::attr(href)').get()[-6:]
            yield item # yield it, it will show in json automatically

        next_page = response.xpath('//a[@class="next_page"]/@href').get() 
        # get the url of next page and go to that page
        if next_page is not None:
            yield response.follow(next_page, self.parse)  # crawl next page
```

## xpath and css
At this time, you may be curious about response.xpath and reponse.css
Because parse is a callback function, so you will get the response in this function and use response to select things
And xpath and css is two selector of Scrapy
Let's firstly see the html
![微信图片_20190625160724.png](https://i.loli.net/2019/06/25/5d122aacb073d28167.png)
The list ```<li></li>```is what we want , it is in the ```<ul id = "jobs">```, so we have following as a list
```python
response.xpath('//div/section/ul[@id="jobs"]/li')

# this will return a list of selector. Only selector can use .css or .xpath
[<Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job" style="background-image:'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job alumni" style="background'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job" style="background-image:'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job" style="background-image:'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job" style="background-image:'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job" style="background-image:'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job" style="background-image:'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job">\n\t\t\t<a href="/jobs/show/'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job founder">\n\t\t\t<a href="/jo'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job founder">\n\t\t\t<a href="/jo'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job founder">\n\t\t\t<a href="/jo'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job alumni">\n\t\t\t<a href="/job'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job alumni">\n\t\t\t<a href="/job'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job alumni">\n\t\t\t<a href="/job'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job alumni">\n\t\t\t<a href="/job'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job alumni">\n\t\t\t<a href="/job'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job alumni">\n\t\t\t<a href="/job'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job">\n\t\t\t<a href="/jobs/show/'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job">\n\t\t\t<a href="/jobs/show/'>,
 <Selector xpath='//div/section/ul[@id="jobs"]/li' data='<li class="job">\n\t\t\t<a href="/jobs/show/'>]
```
**Why is //div, as I think, it means no matter how many tags before it. So xpath means when the path in this html equal to what we give it will give correct answers.**


After we get each ```<li></li>```, we can use .css or .xpath continue to select things
Analze the html of one list item
```
<li class="job" style="background-image: url('/system/logos/21589/medium/Logo_Klassisch.png');">
			<a href="/jobs/show/196129">
				<strong>Werkstudent als Junior Consultant Automotive (m/w/d) </strong><br />
				Werkstudent in München<br />
				bei StreetScooter Research GmbH<br />
				<time datetime="2019-06-05">05.06.2019</time>
			</a>
		</li>
```
You will got
```python
item['name'] = sel.css('strong::text').get() 
# ::text means we want to get the textnote, Don't forget to add get, otherwise it will be only a selector
```
```python
trans_table = {ord(c): None for c in u'\r\n\t'}  # To remove \r\n\t in the output
item['description']= ' '.join(s.translate(trans_table) for s in sel.css('a::text').getall())
```
```python
item['time'] = sel.css('time::text').get()
item['id'] = sel.css('a::attr(href)').get()[-6:] # get attribute "href" of a tag
```
yield them!
If you want to test xpath and css, open terminal ,type
```python
scrapy shell "https://******/jobs/search?utf8=%E2%9C%93&search%5Bq%5D=java"
```
If you want to know more about selector, go to seehttps://docs.scrapy.org/en/latest/topics/item-pipeline.html

# Output
Finally ,open ternimal and type
```
scrapy crawl tumjob -o items.json -a keywords=werkstudent
```
You will get output in item.json.

Thanks, If any error, contact me
https://github.com/Kailiangdong/Scrapy_Crawler_Practise