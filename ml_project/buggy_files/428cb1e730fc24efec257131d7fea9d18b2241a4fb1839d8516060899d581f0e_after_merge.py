    def sanitize(value):
        value = value.strip('.')
        if value:
            try:
                return value.encode('idna').decode().lower()
            except UnicodeError:
                return