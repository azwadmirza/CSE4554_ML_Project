def add_username_and_pass_to_url(url, username, passwd):
    url_parts = parse_url(url)._asdict()
    url_parts['auth'] = username + ':' + quote(passwd, '')
    return Url(**url_parts).url