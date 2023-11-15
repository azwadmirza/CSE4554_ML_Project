    def _data_loader(self):
        try:
            value = getattr(self, attr_name)
        except AttributeError:
            try:
                value = fn(self)  # Lazy evaluation, done only once.
            except AttributeError as e:
                # Guard against AttributeError suppression. (Issue #142)
                raise RuntimeError('An AttributeError was encountered: ' + str(e)) from e
            setattr(self, attr_name, value)  # Memoize evaluation.
        return value