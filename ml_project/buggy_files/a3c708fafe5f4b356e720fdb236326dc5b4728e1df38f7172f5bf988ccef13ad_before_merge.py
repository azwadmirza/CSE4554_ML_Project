    def get(self, name: str, *, dummy: bool = False) -> GQLBaseType:
        '''Get a special GQL type either by name or based on EdgeDB type.'''
        # normalize name and possibly add 'edb_base' to kwargs
        edb_base = None
        kwargs: Dict[str, Any] = {'dummy': dummy}

        if not name.startswith('stdgraphql::'):
            if edb_base is None:
                type_id = s_types.type_id_from_name(
                    s_name.name_from_string(name))
                if type_id is not None:
                    edb_base = self.edb_schema.get_by_id(
                        type_id,
                        type=s_types.Type,
                    )
                elif '::' in name:
                    edb_base = self.edb_schema.get(
                        name,
                        type=s_types.Type,
                    )
                else:
                    for module in self.modules:
                        edb_base = self.edb_schema.get(
                            f'{module}::{name}',
                            type=s_types.Type,
                            default=None,
                        )
                        if edb_base:
                            break

                    if edb_base is None:
                        raise AssertionError(
                            f'unresolved type: {module}::{name}')

            kwargs['edb_base'] = edb_base

        # check if the type already exists
        fkey = (name, dummy)
        gqltype = self._type_map.get(fkey)

        if not gqltype:
            _type = GQLTypeMeta.edb_map.get(name, GQLShadowType)
            gqltype = _type(schema=self, **kwargs)
            self._type_map[fkey] = gqltype

        return gqltype