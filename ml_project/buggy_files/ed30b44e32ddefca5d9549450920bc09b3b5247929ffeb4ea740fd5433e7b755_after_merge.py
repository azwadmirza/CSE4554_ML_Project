            def keys_check(event):
                if event.key is not None:
                    use_name = event.key.name.lower()
                    if use_name in self._keys_check:
                        self._keys_check[use_name]()