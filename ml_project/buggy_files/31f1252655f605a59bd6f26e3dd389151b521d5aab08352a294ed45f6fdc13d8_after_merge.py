def _datavalue(datatype, data):
    if datatype == 'try_int':
        try:
            return int(data)
        except ValueError:
            return None
    elif datatype is tuple and datatype[0] == 're_int':
        search = re.search(datatype[1], data)
        if search:
            try:
                return int(search.group(1))
            except ValueError:
                return None
        return None
    else:
        return data