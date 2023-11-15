def _search(prefix="latest/"):
    '''
    Recursively look up all grains in the metadata server
    '''
    ret = {}
    linedata = http.query(os.path.join(HOST, prefix), headers=True)
    if 'body' not in linedata:
        return ret
    if linedata['headers'].get('Content-Type', 'text/plain') == 'application/octet-stream':
        return linedata['body']
    for line in linedata['body'].split('\n'):
        if line.endswith('/'):
            ret[line[:-1]] = _search(prefix=os.path.join(prefix, line))
        elif prefix == 'latest/':
            # (gtmanfred) The first level should have a forward slash since
            # they have stuff underneath. This will not be doubled up though,
            # because lines ending with a slash are checked first.
            ret[line] = _search(prefix=os.path.join(prefix, line + '/'))
        elif line.endswith(('dynamic', 'meta-data')):
            ret[line] = _search(prefix=os.path.join(prefix, line))
        elif '=' in line:
            key, value = line.split('=')
            ret[value] = _search(prefix=os.path.join(prefix, key))
        else:
            retdata = http.query(os.path.join(HOST, prefix, line)).get('body', None)
            # (gtmanfred) This try except block is slightly faster than
            # checking if the string starts with a curly brace
            try:
                ret[line] = salt.utils.json.loads(retdata)
            except ValueError:
                ret[line] = retdata
    return ret