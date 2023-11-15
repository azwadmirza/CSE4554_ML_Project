        def __getattr__(self, attribute):
            """Delegate __getattr__ to the original descriptor and/or
            comparator."""
            try:
                return getattr(descriptor, attribute)
            except AttributeError:
                if attribute == "comparator":
                    raise AttributeError("comparator")
                try:
                    # comparator itself might be unreachable
                    comparator = self.comparator
                except AttributeError:
                    raise AttributeError(
                        "Neither %r object nor unconfigured comparator "
                        "object associated with %s has an attribute %r"
                        % (type(descriptor).__name__, self, attribute)
                    )
                else:
                    try:
                        return getattr(comparator, attribute)
                    except AttributeError:
                        raise AttributeError(
                            "Neither %r object nor %r object "
                            "associated with %s has an attribute %r"
                            % (
                                type(descriptor).__name__,
                                type(comparator).__name__,
                                self,
                                attribute,
                            )
                        )