    def sanitize(value):
        value = value.strip('.')
        if value:
            return value.encode('idna').decode().lower()