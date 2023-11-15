    def sanitize(value):
        value = value.rstrip('.')
        if value:
            return value.encode('idna').decode().lower()