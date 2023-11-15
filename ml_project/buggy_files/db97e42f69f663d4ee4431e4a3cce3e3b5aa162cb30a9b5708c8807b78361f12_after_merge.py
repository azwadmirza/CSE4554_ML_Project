async def checkData(tweet, location, config, conn):
    usernames = []
    copyright = tweet.find("div", "StreamItemContent--withheld")
    if copyright is None and is_tweet(tweet):
        tweet = Tweet(tweet, location, config)

        if not tweet.datestamp:
            print("[x] Hidden tweet found, account suspended due to violation of TOS")
            return

        if datecheck(tweet.datestamp, config):
            output = format.Tweet(config, tweet)

            if config.Database:
                db.tweets(conn, tweet, config)

            if config.Pandas:
                panda.update(tweet, config)

            if config.Store_object:
                tweets_object.append(tweet)

            if config.Elasticsearch:
                elasticsearch.Tweet(tweet, config)

            _output(tweet, output, config)