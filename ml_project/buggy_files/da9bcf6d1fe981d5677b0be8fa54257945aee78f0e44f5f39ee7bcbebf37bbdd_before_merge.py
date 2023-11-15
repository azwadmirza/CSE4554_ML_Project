    def get_redirected(url):
        # Returns false if url is not right
        headers = {'User-Agent': 'Mozilla/5.0'}
        request = urllib2.Request(url, headers=headers)
        try:
            return urllib2.urlopen(request).geturl()
        except urllib2.URLError:
            LOG.error("Can't reach struts2 server")
            return False