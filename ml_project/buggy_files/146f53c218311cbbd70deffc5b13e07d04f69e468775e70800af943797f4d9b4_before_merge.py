def get_chrome_bookmark_urls(path):
    """Return a list of bookmarked URLs in Google Chrome/Chromium"""
    import json

    # read file to parser
    with open(path, 'r') as f:
        js = json.load(f)

    # empty list
    urls = []

    # local recursive function
    def get_chrome_bookmark_urls_helper(node):
        if not isinstance(node, dict):
            return
        if 'type' not in node:
            return
        if node['type'] == "folder":
            # folders have children
            for child in node['children']:
                get_chrome_bookmark_urls_helper(child)
        if node['type'] == "url" and 'url' in node:
            urls.append(node['url'])

    # find bookmarks
    for node in js['roots']:
        get_chrome_bookmark_urls_helper(js['roots'][node])

    return list(set(urls))  # unique