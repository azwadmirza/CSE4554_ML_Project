def _datavalue(datatype, data):
    if datatype == 'int':
        return int(data)
    elif datatype and datatype[0] == 're_int':
        return int(re.search(datatype[1], data).group(1))
    else:
        return data