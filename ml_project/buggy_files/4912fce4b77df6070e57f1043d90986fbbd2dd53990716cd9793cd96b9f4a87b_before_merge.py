def _output(obj, output, config):
    if config.Output != None:
        if config.Store_csv:
            write.Csv(obj, config)
        elif config.Store_json:
            write.Json(obj, config)
        else:
            write.Text(output, config.Output)
            
    if config.Pandas:
        Pandas.update(obj, config.Essid)

    if config.Elasticsearch:
        if config.Store_object:
            tweets_object.append(obj)
        else:
            print(output, end=".", flush=True)
    else:
        if config.Store_object:
            tweets_object.append(obj)
        else:
            print(output)