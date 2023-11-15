    def __init__(self, *args, **kwargs: Dict[str, Any]):
        if args:
            if len(args) == 1 and isinstance(args[0], dict):
                kwargs.update(args[0])
            else:
                message = (
                    'Only one dictionary as positional argument is allowed')
                raise ValueError(message)
        super().__init__(**kwargs)
        self.images = [
            (k, v) for (k, v) in self.items()
            if isinstance(v, Image)
        ]
        self._parse_images(self.images)
        self.update_attributes()  # this allows me to do e.g. subject.t1
        self.history = []