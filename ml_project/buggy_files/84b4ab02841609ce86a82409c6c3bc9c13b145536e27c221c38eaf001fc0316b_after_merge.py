    def _populate_sub_fields(self):
        # typing interface is horrible, we have to do some ugly checks
        if isinstance(self.type_, type) and issubclass(self.type_, JsonWrapper):
            self.type_ = self.type_.inner_type
            self.parse_json = True

        origin = getattr(self.type_, '__origin__', None)
        if origin is None:
            # field is not "typing" object eg. Union, Dict, List etc.
            return
        if origin is Union:
            types_ = []
            for type_ in self.type_.__args__:
                if type_ is NoneType:
                    self.allow_none = True
                    self.required = False
                else:
                    types_.append(type_)
            self.sub_fields = [self._create_sub_type(t, f'{self.name}_{display_as_type(t)}') for t in types_]
            return

        if issubclass(origin, Tuple):
            self.shape = Shape.TUPLE
            self.sub_fields = [
                self._create_sub_type(t, f'{self.name}_{i}') for i, t in enumerate(self.type_.__args__)
            ]
            return

        if issubclass(origin, List):
            self.type_ = self.type_.__args__[0]
            self.shape = Shape.LIST
        elif issubclass(origin, Set):
            self.type_ = self.type_.__args__[0]
            self.shape = Shape.SET
        else:
            assert issubclass(origin, Mapping)
            self.key_field = self._create_sub_type(self.type_.__args__[0], 'key_' + self.name)
            self.type_ = self.type_.__args__[1]
            self.shape = Shape.MAPPING

        if getattr(self.type_, '__origin__', None):
            # type_ has been refined eg. as the type of a List and sub_fields needs to be populated
            self.sub_fields = [self._create_sub_type(self.type_, '_' + self.name)]