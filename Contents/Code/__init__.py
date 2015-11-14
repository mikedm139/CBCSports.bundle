PREFIX = '/video/cbcsports'
NAME = 'CBC Sports'

BASE_URL = 'http://www.cbc.ca'
LIVE_URL = BASE_URL + '/player/sports/Live'

####################################################################################################
def Start():
  ObjectContainer.title1 = NAME
  ObjectContainer.art = R('art-default.jpg')
  DirectoryObject.thumb = R('icon-default.png')
  
####################################################################################################
@handler(PREFIX, NAME, "icon-default.png", "art-default.jpg")
def MainMenu():
  oc = ObjectContainer()
  page = HTML.ElementFromURL(LIVE_URL)
  for item in page.xpath('//section[@class="category-content full"]//li[@class="medialist-item"]'):
    link = item.xpath('./a')[0].get('href')
    thumb = item.xpath('.//img')[0].get('src')
    date = item.xpath('.//span[@class="medialist-date"]')[0].text
    title = item.xpath('.//div[@class="medialist-title"]')[0].text
    oc.add(
      VideoClipObject(
        url = link,
        title = title,
        originally_available_at = Datetime.ParseDate(date).date(),
        thumb = Resource.ContentsOfURLWithFallback(url=thumb)
        )
    )
  return oc

