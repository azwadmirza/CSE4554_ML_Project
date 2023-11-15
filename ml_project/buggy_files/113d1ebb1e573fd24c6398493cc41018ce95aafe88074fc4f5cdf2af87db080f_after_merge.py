    def __filter_fields(self, field_names, obj, many=False):
        """Return only those field_name:field_obj pairs specified by
        ``field_names``.

        :param set field_names: Field names to include in the final
            return dictionary.
        :returns: An dict of field_name:field_obj pairs.
        """
        if obj and many:
            try:  # Homogeneous collection
                # Prefer getitem over iter to prevent breaking serialization
                # of objects for which iter will modify position in the collection
                # e.g. Pymongo cursors
                if hasattr(obj, '__getitem__') and callable(getattr(obj, '__getitem__')):
                    try:
                        obj_prototype = obj[0]
                    except KeyError:
                        obj_prototype = next(iter(obj))
                else:
                    obj_prototype = next(iter(obj))
            except (StopIteration, IndexError):  # Nothing to serialize
                return dict((k, v) for k, v in self.declared_fields.items() if k in field_names)
            obj = obj_prototype
        ret = self.dict_class()
        for key in field_names:
            if key in self.declared_fields:
                ret[key] = self.declared_fields[key]
            else:  # Implicit field creation (class Meta 'fields' or 'additional')
                if obj:
                    attribute_type = None
                    try:
                        if isinstance(obj, Mapping):
                            attribute_type = type(obj[key])
                        else:
                            attribute_type = type(getattr(obj, key))
                    except (AttributeError, KeyError) as err:
                        err_type = type(err)
                        raise err_type(
                            '"{0}" is not a valid field for {1}.'.format(key, obj))
                    field_obj = self.TYPE_MAPPING.get(attribute_type, fields.Field)()
                else:  # Object is None
                    field_obj = fields.Field()
                # map key -> field (default to Raw)
                ret[key] = field_obj
        return ret