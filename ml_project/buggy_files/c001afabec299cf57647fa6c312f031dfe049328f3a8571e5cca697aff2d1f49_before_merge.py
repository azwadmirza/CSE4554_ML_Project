    def __init__(self, *args):
        """
        Creates a new MetaDict instance.
        """
        # Store all keys as lower-case to allow for case-insensitive indexing
        # OrderedDict can be instantiated from a list of lists or a tuple of tuples
        tags = dict()
        if args:
            args = list(args)
            adict = args[0]
            if isinstance(adict, list) or isinstance(adict, tuple):
                items = adict
            elif isinstance(adict, dict):
                items = adict.items()
            else:
                raise TypeError(f"Can not create a MetaDict from this input of type {type(adict)}")

            self._check_str_keys(items)
            tags = OrderedDict((k.lower(), v) for k, v in items)
            args[0] = tags

        super().__init__(*args)

        # Use `copy=True` to avoid mutating the caller's keycomments
        # dictionary (if they provided one).
        self._prune_keycomments(copy=True)