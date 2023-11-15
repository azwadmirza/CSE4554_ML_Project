def update(object, config):
    global _type

    try:
        _type = ((object.type == "tweet")*"tweet" +
                 (object.type == "user")*"user")
    except AttributeError:
        _type = config.Following*"following" + config.Followers*"followers"

    if _type == "tweet":
        dt = f"{object.datestamp} {object.timestamp}"
        _data = {
            "id": object.id,
            "date": dt,
            "timezone": object.timezone,
            "location": object.location,
            "tweet": object.tweet,
            "hashtags": object.hashtags,
            "user_id": object.user_id,
            "username": object.username,
            "link": object.link,
            "retweet": object.retweet,
            "user_rt": object.user_rt,
            "essid": config.Essid,
            'mentions': object.mentions
            }
        _object_blocks[_type].append(_data)
    elif _type == "user":
        _data = {
            "id": object.id,
            "name": object.name,
            "username": object.username,
            "bio": object.bio,
            "location": object.location,
            "url": object.url,
            "join_datetime": object.join_date + " " + object.join_time,
            "join_date": object.join_date,
            "join_time": object.join_time,
            "tweets": object.tweets,
            "following": object.following,
            "followers": object.followers,
            "likes": object.likes,
            "media": object.media_count,
            "private": object.is_private,
            "verified": object.is_verified,
            "avatar": object.avatar,
            "session": str(config.Essid)
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