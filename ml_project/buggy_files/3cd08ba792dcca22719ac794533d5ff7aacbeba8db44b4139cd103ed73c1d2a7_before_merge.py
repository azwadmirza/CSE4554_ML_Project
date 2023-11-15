    def __init__(self, message: Union[dict, tuple] = (), auto: bool = False,
                 harmonization: dict = None) -> None:
        try:
            classname = message['__type'].lower()
            del message['__type']
        except (KeyError, TypeError):
            classname = self.__class__.__name__.lower()

        if harmonization is None:
            harmonization = utils.load_configuration(HARMONIZATION_CONF_FILE)
        try:
            self.harmonization_config = harmonization[classname]
        except KeyError:
            raise exceptions.InvalidArgument('__type',
                                             got=classname,
                                             expected=VALID_MESSSAGE_TYPES,
                                             docs=HARMONIZATION_CONF_FILE)

        if (classname == 'event' and 'extra' in self.harmonization_config and
           self.harmonization_config['extra']['type'] == 'JSON'):
            warnings.warn("Assuming harmonization type 'JSONDict' for harmonization field 'extra'. "
                          "This assumption will be removed in version 3.0.", DeprecationWarning)
            self.harmonization_config['extra']['type'] = 'JSONDict'
        for harm_key in self.harmonization_config.keys():
            if not re.match('^[a-z_](.[a-z_0-9]+)*$', harm_key) and harm_key != '__type':
                raise exceptions.InvalidKey("Harmonization key %r is invalid." % harm_key)

        super().__init__()
        if isinstance(message, dict):
            iterable = message.items()
        elif isinstance(message, tuple):
            iterable = message
        else:
            raise ValueError("Type %r of message can't be handled, must be dict or tuple.", type(message))
        for key, value in iterable:
            if not self.add(key, value, sanitize=False, raise_failure=False):
                self.add(key, value, sanitize=True)