    def is_valid(value, sanitize=False):
        if sanitize:
            value = GenericType().sanitize(value)
            value = FQDN().sanitize(value)

        if not GenericType().is_valid(value):
            return False

        if value.strip('.') != value or value != value.lower():
            return False

        if IPAddress().is_valid(value):
            return False

        url = parse.urlsplit(value)
        if (url.scheme != '' or url.netloc != '' or url.query != '' or url.fragment != '' or
           url.path.find('/') >= 0):
            return False

        if value.encode('idna').decode() != value:
            return False

        return True