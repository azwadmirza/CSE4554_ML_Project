def try_get(keys, dictionary):
    for key in keys:
        if key in dictionary:
            ret = dictionary[key]
            if type(ret) == list:
                ret = ret[0]
            return ret
    return None