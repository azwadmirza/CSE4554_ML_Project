    def process_bind_param(self, value, dialect):
        try:
            localpart, domain_name = value.split('@')
            return "{0}@{1}".format(
                localpart,
                idna.encode(domain_name).decode('ascii'),
            )
        except ValueError:
            pass