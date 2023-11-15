    def _append_writer(self, path, schema=None, add_args=None, add_kwargs=None):
        # Add additional args and kwargs
        _args = add_args or []
        _kwargs = tlz.merge(self.pwriter_kwargs, add_kwargs or {})

        if self.bytes_io:
            bio = BytesIO()
            self.data_bios.append(bio)
            self.data_writers.append(self.pwriter(bio, *_args, **_kwargs))
        else:
            self.data_writers.append(self.pwriter(path, *_args, **_kwargs))