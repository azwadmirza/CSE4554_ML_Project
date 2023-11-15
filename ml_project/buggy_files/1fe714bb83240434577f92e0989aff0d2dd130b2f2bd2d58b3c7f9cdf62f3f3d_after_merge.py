def update(object, config):
    global _type

    try:
        _type = ((object.type == "tweet")*"tweet" +
                 (object.type == "user")*"user")
    except AttributeError:
        _type = config.Following*"following" + config.Followers*"followers"

    if _type == "tweet":
        Tweet = object
        day = weekdays[strftime("%A", localtime(Tweet.datetime))]
        dt = f"{object.datestamp} {object.timestamp}"
        _data = {
            "id": str(Tweet.id),
            "conversation_id": Tweet.conversation_id,
            "created_at": Tweet.datetime,
            "date": dt,
            "timezone": Tweet.timezone,
            "place": Tweet.place,
            "location": Tweet.location,
            "tweet": Tweet.tweet,
            "hashtags": Tweet.hashtags,
            "user_id": Tweet.user_id,
            "user_id_str": Tweet.user_id_str,
            "username": Tweet.username,
            "name": Tweet.name,
            "profile_image_url": Tweet.profile_image_url,
            "day": day,
            "hour": hour(Tweet.datetime),
            "link": Tweet.link,
            "gif_url": Tweet.gif_url,
            "gif_thumb": Tweet.gif_thumb,
            "video_url": Tweet.video_url,
            "video_thumb": Tweet.video_thumb,
            "is_reply_to": Tweet.is_reply_to,
            "has_parent_tweet": Tweet.has_parent_tweet,
            "retweet": Tweet.retweet,
            "nlikes": int(Tweet.likes_count),
            "nreplies": int(Tweet.replies_count),
            "nretweets": int(Tweet.retweets_count),
            "is_quote_status": Tweet.is_quote_status,
            "quote_id": Tweet.quote_id,
            "quote_id_str": Tweet.quote_id_str,
            "quote_url": Tweet.quote_url,
            "search": str(config.Search),
            "near": config.Near
            }
        _object_blocks[_type].append(_data)
    elif _type == "user":
        user = object
        _data = {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "bio": user.bio,
            "location": user.location,
            "url": user.url,
            "join_datetime": user.join_date + " " + user.join_time,
            "join_date": user.join_date,
            "join_time": user.join_time,
            "tweets": user.tweets,
            "following": user.following,
            "followers": user.followers,
            "likes": user.likes,
            "media": user.media_count,
            "private": user.is_private,
            "verified": user.is_verified,
            "avatar": user.avatar,
            "background_image": user.background_image,
            }
        _object_blocks[_type].append(_data)
    elif _type == "followers" or _type == "following":
        _data = {
            config.Following*"following" + config.Followers*"followers" :
                             {config.Username: object[_type]}
        }
        _object_blocks[_type] = _data
    else:
        print("Wrong type of object passed!")