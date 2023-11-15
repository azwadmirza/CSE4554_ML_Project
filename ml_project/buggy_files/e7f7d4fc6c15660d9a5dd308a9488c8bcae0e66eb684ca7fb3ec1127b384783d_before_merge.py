def add_username_and_pass_to_url(url, username, passwd):
    url_obj = parse_url(url)
    url_obj.auth = username + ':' + quote(passwd, '')
    return url_obj.url