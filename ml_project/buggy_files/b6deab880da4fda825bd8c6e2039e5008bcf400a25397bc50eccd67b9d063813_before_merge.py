def getYoutubePosts(ids):
    videos = []
    with FuturesSession() as session:
        futures = [session.get('https://www.youtube.com/feeds/videos.xml?channel_id={id}'.format(id=id.channelId)) for id in ids]
        for future in as_completed(futures):
            resp = future.result()
            rssFeed=feedparser.parse(resp.content)
            for vid in rssFeed.entries:
                time = datetime.datetime.now() - datetime.datetime(*vid.published_parsed[:6])

                if time.days >=7:
                    continue
                
                video = ytPost()
                video.date = vid.published_parsed
                video.timeStamp = getTimeDiff(vid.published_parsed)
                video.channelName = vid.author_detail.name
                video.channelId = vid.yt_channelid
                video.channelUrl = vid.author_detail.href
                video.id = vid.yt_videoid
                video.videoTitle = vid.title
                video.videoThumb = vid.media_thumbnail[0]['url'].replace('/', '~')
                video.views = vid.media_statistics['views']
                video.description = vid.summary_detail.value
                video.description = re.sub(r'^https?:\/\/.*[\r\n]*', '', video.description[0:120]+"...", flags=re.MULTILINE)
                videos.append(video)
    return videos