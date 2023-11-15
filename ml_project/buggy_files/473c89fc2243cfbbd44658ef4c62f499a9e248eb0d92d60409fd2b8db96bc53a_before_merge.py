def display(api_key, url, return_formatted=True):
    """
    Sends an API GET request and acts as a generic formatter for the JSON response.
    """
    try:
        r = get(api_key, url)
    except HTTPError as e:
        print(e)
        print(e.read(1024))  # Only return the first 1K of errors.
        sys.exit(1)
    if not return_formatted:
        return r
    elif type(r) == list:
        # Response is a collection as defined in the REST style.
        print('Collection Members')
        print('------------------')
        for n, i in enumerate(r):
            # All collection members should have a name in the response.
            # url is optional
            if 'url' in i:
                print('#%d: %s' % (n + 1, i.pop('url')))
            if 'name' in i:
                print('  name: %s' % i.pop('name'))
            for k, v in i.items():
                print(f'  {k}: {v}')
        print('')
        print('%d element(s) in collection' % len(r))
    elif type(r) == dict:
        # Response is an element as defined in the REST style.
        print('Member Information')
        print('------------------')
        for k, v in r.items():
            print(f'{k}: {v}')
    elif type(r) == str:
        print(r)
    else:
        print('response is unknown type: %s' % type(r))