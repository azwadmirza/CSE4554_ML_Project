        def __getattr__(self, attribute):
            """Delegate __getattr__ to the original descriptor and/or
            comparator."""

            try:
                return getattr(descriptor, attribute)
            except AttributeError:
                try:
                    return getattr(self.comparator, attribute)
                except AttributeError:
                    raise AttributeError(
                        "Neither %r object nor %r object associated with %s "
                        "has an attribute %r"
                        % (
                            type(descriptor).__name__,
                            type(self.comparator).__name__,
                            self,
                            attribute,
                        )
                    )