    def get_field_info(cls, name: str) -> Dict[str, Any]:
        field_info = cls.fields.get(name) or {}
        if isinstance(field_info, str):
            field_info = {'alias': field_info}
        elif cls.alias_generator and 'alias' not in field_info:
            alias = cls.alias_generator(name)
            if not isinstance(alias, str):
                raise TypeError(f'Config.alias_generator must return str, not {type(alias)}')
            field_info['alias'] = alias
        return field_info