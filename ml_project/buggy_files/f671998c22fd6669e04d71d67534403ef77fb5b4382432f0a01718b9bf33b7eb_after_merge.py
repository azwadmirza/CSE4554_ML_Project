def _output(obj, output, config, **extra):
    #logging.info("[<] " + str(datetime.now()) + ':: output+_output')
    if config.Lowercase:
        if isinstance(obj, str):
            obj = obj.lower()
        elif str(type(obj)) == "<class 'twint.user.user'>":
            pass
        else:
            obj.username = obj.username.lower()
            for i in range(len(obj.mentions)):
                obj.mentions[i] = obj.mentions[i]["screen_name"].lower()
            for i in range(len(obj.hashtags)):
                obj.hashtags[i] = obj.hashtags[i].lower()
    if config.Output != None:
        if config.Store_csv:
            try :
                write.Csv(obj, config)
            except Exception as e:
                print(str(e) + " [x] output._output")
        elif config.Store_json:
            write.Json(obj, config)
        else:
            write.Text(output, config.Output)

    if config.Pandas and obj.type == "user":
        panda.update(obj, config)
    if extra.get("follow_list"):
        follow_object.username = config.Username
        follow_object.action = config.Following*"following" + config.Followers*"followers"
        follow_object.users = _follow_list
        panda.update(follow_object, config.Essid)
    if config.Elasticsearch:
        print("", end=".", flush=True)
    else:
        if config.Store_object:
            tweets_object.append(obj)
        else:
            if not config.Hide_output:
                try:
                    print(output)
                except UnicodeEncodeError:
                    print("unicode error [x] output._output")