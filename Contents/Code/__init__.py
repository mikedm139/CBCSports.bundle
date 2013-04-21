PREFIX = '/video/cbcsports'
NAME = 'CBC Sports'

BASE_URL = 'http://www.cbc.ca'
VIDEO_URL = BASE_URL + '/sports/%svideo/#id=%s'
LIVE_URL = BASE_URL + '/sports/video/live/#id=%s'
LIVE_ID = '1248955900'
LIVE_JSON = 'http://feed.theplatform.com/f/h9dtGB/r3VD0FujBumK?form=json&fields=categories,content,defaultThumbnailUrl,description,pubDate,title,:event,:genre,:league,:liveOndemand,:seasonNumber,:segment,:show,:sport,:sportGroup,:type,:unapprovedDate,:playerName,:playerID,:awayTeam,:homeTeam,:yearOfGame,:dateOfGame,:gameID,:time&releaseFields=approved,id,url&count=true&sort=pubDate&byApproved=true&byCategoryIds=1248955900&range=1-12'
JSON_URL = 'http://feed.theplatform.com/f/h9dtGB/r3VD0FujBumK?form=json&fields=categories,content,defaultThumbnailUrl,description,pubDate,title,:event,:genre,:league,:liveOndemand,:seasonNumber,:segment,:show,:sport,:sportGroup,:type,:unapprovedDate,:playerName,:playerID,:awayTeam,:homeTeam,:yearOfGame,:dateOfGame,:gameID,:time&releaseFields=approved,id,url&count=true&byApproved=true&sort=pubDate&byCategoryIds='
RANGE = '&range=%d-%d'
PAGE_SIZE = 20

RE_SERIES_ID = Regex('var="seriesWatchPlaylistId" value="([0-9]+)"')
RE_PLAYLISTS = Regex("(playlists: \[ { .+ } \])")

####################################################################################################
def Start():
  ObjectContainer.title1 = NAME
  ObjectContainer.art = R('art-default.jpg')
  DirectoryObject.thumb = R('icon-default.png')
  
####################################################################################################
@handler(PREFIX, NAME, "icon-default.png", "art-default.jpg")
def MainMenu():
  oc = ObjectContainer()
  if Client.Platform in ['Windows', 'MacOSX']:
    Log("Client.Platform = %s. Live Streaming supported." % Client.Platform)
    json = JSON.ObjectFromURL(JSON_URL + LIVE_ID + RANGE % (0,1))
    live_stream = json['entries'][0]
    start = int(float(live_stream['pubDate'])/1000)
    now = int(Datetime.TimestampFromDatetime(Datetime.Now()))
    end = int(float(live_stream['pubDate'])/1000) + int(live_stream['media$content'][0]['plfile$duration'])
    title = live_stream['title']
    summary = live_stream['description']
    thumb = live_stream['plmedia$defaultThumbnailUrl']
    if start < now < end:
      liveId = live_stream['media$content'][1]['plfile$releases'][0]['id'].split('/')[-1]
      oc.add(VideoClipObject(url = LIVE_URL % liveId, title = "LIVE: " + title,
        summary = summary, originally_available_at=Datetime.FromTimestamp(start),
        thumb = Resource.ContentsOfURLWithFallback(thumb)))
    else:
      oc.add(DirectoryObject(key=Callback(LiveUpNext, title, start), title = "Coming up: " + title,
        summary = Datetime.TimestampFromDatetime(start), thumb = Resource.ContentsOfURLWithFallback(thumb)))
  data = HTML.ElementFromURL(BASE_URL + '/sports/video')
  for sport in data.xpath('//select[@name="pageselect"]//option'):
    title = sport.text
    href = sport.get('value')
    if len(href) > 0:
      oc.add(DirectoryObject(key=Callback(Categories, title=title, href=href), title=title))
  return oc

####################################################################################################
@route(PREFIX + '/categories')
def Categories(title, href):
  oc = ObjectContainer(title2=title)
  content = HTTP.Request(BASE_URL + href).content
  categories = RE_PLAYLISTS.search(content).group(1)
  '''the json is not well formatted for our purposes so, we need to doctor it a little bit'''
  categories = '{'+categories.replace("playlists", "'playlists'").replace("title","'title'").replace("categoryId","'categoryId'").replace("sortField","'SortField'")+'}'
  categories_json =  JSON.ObjectFromString(categories)
  for category in categories_json['playlists']:
    categoryTitle = category['title']
    if categoryTitle == 'Audio': continue
    categoryId = category['categoryId']
    oc.add(DirectoryObject(key=Callback(VideoMenu, title=title, categoryId=categoryId), title=categoryTitle))
  return oc

####################################################################################################
@route(PREFIX + '/videos')
def VideoMenu(title, categoryId, offset=0):
    oc = ObjectContainer(title2=title)
    json = JSON.ObjectFromURL(JSON_URL + categoryId + RANGE % (int(offset), int(offset)+int(PAGE_SIZE)))
    for video in json['entries']:
      video_title = video['title']
      summary = video['description']
      duration = int(float(video['media$content'][0]['plfile$duration'])*1000)
      thumb = video['plmedia$defaultThumbnailUrl']
      video_id = video['media$content'][0]['plfile$releases'][0]['id'].split('/')[-1]
      date = Datetime.FromTimestamp(float(video['pubDate'])/1000).date()
      if 'Punjabi' in summary:
        video_url = VIDEO_URL % ('punjabi/', video_id)
      else:
        video_url = VIDEO_URL % ('', video_id)
      oc.add(VideoClipObject(url=video_url, title=video_title, summary=summary, duration=duration, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(thumb)))
    if int(json['totalResults']) > offset:
      oc.add(NextPageObject(key=Callback(VideoMenu, title=title, categoryId=categoryId, offset=int(offset)+int(PAGE_SIZE))))
    return oc