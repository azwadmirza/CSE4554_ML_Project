    def expand_extensions(self):
        for connection in (self.compute_conn, self.volume_conn):
            if connection is None:
                continue
            for extension in self.extensions:
                for attr in extension.module.__dict__:
                    if not inspect.isclass(getattr(extension.module, attr)):
                        continue
                    for key, value in six.iteritems(connection.__dict__):
                        if not isinstance(value, novaclient.base.Manager):
                            continue
                        if value.__class__.__name__ == attr:
                            setattr(connection, key, getattr(connection, extension.name))