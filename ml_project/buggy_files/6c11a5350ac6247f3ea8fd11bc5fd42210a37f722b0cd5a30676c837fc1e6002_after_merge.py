def update(Tweet, session):
    day = weekday(strftime("%A", localtime(Tweet.datetime)))
    dt = "{} {}".format(Tweet.datestamp, Tweet.timestamp)

    _data = {
                "id": Tweet.id,
                "date": dt,
                "timezone": Tweet.timezone,
                "location": Tweet.location,
                "tweet": Tweet.tweet,
                "hashtags": Tweet.hashtags,
                "user_id": Tweet.user_id,
                "username": Tweet.username,
                "day": day,
                "hour": hour(Tweet.datetime),
                "link": Tweet.link,
                "retweet": Tweet.retweet,
                "user_rt": Tweet.user_rt,
                "essid": str(session),
                'mentions': Tweet.mentions
                }
    _blocks.append(_data)