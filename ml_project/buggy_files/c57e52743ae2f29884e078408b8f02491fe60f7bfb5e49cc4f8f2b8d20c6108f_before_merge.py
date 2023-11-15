    def add(self, key: str, value: str, sanitize: bool = True,
            overwrite: Optional[bool] = None, ignore: Sequence = (),
            raise_failure: bool = True) -> Optional[bool]:
        """
        Add a value for the key (after sanitation).

        Parameters:
            key: Key as defined in the harmonization
            value: A valid value as defined in the harmonization
                If the value is None or in _IGNORED_VALUES the value will be ignored.
                If the value is ignored, the key exists and overwrite is True, the key
                is deleted.
            sanitize: Sanitation of harmonization type will be called before validation
                (default: True)
            overwrite: Overwrite an existing value if it already exists (default: None)
                If True, overwrite an existing value
                If False, do not overwrite an existing value
                If None, raise intelmq.exceptions.KeyExists for an existing value
            raise_failure: If a intelmq.lib.exceptions.InvalidValue should be raised for
                invalid values (default: True). If false, the return parameter will be
                False in case of invalid values.

        Returns:
            * True if the value has been added.
            * False if the value is invalid and raise_failure is False or the value existed
                and has not been overwritten.
            * None if the value has been ignored.

        Raises:
            intelmq.lib.exceptions.KeyExists: If key exists and won't be overwritten explicitly.
            intelmq.lib.exceptions.InvalidKey: if key is invalid.
            intelmq.lib.exceptions.InvalidArgument: if ignore is not list or tuple.
            intelmq.lib.exceptions.InvalidValue: If value is not valid for the given key and
                raise_failure is True.
        """
        if overwrite is None and key in self:
            raise exceptions.KeyExists(key)
        if overwrite is False and key in self:
            return False

        if value is None or value in self._IGNORED_VALUES:
            if overwrite and key in self:
                del self[key]
            return

        if not self.__is_valid_key(key):
            raise exceptions.InvalidKey(key)

        try:
            if value in ignore:
                return
        except TypeError:
            raise exceptions.InvalidArgument('ignore',
                                             got=type(ignore),
                                             expected='list or tuple')

        if sanitize and not key == '__type':
            old_value = value
            value = self.__sanitize_value(key, value)
            if value is None:
                if raise_failure:
                    raise exceptions.InvalidValue(key, old_value)
                else:
                    return False

        valid_value = self.__is_valid_value(key, value)
        if not valid_value[0]:
            if raise_failure:
                raise exceptions.InvalidValue(key, value, reason=valid_value[1])
            else:
                return False

        class_name, subitem = self.__get_type_config(key)
        if class_name and class_name['type'] == 'JSONDict' and not subitem:
            # for backwards compatibility allow setting the extra field as string
            if overwrite and key in self:
                del self[key]
            for extrakey, extravalue in json.loads(value).items():
                # For extra we must not ignore empty or invalid values because of backwards compatibility issues #1335
                if key != 'extra' and hasattr(extravalue, '__len__'):
                    if not len(extravalue):  # ignore empty values
                        continue
                if key != 'extra' and extravalue in self._IGNORED_VALUES:
                    continue
                super().__setitem__('{}.{}'.format(key, extrakey),
                                    extravalue)
        else:
            super().__setitem__(key, value)
        return True