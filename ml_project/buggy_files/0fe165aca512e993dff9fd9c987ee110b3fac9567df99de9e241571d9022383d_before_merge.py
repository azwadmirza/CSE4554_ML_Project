        def store_overloads_on_success():
            # use to ensure overloads are stored on success
            try:
                yield
            except:
                raise
            else:
                exists = self.overloads.get(cres.signature)
                if exists is None:
                    self.overloads[cres.signature] = cres