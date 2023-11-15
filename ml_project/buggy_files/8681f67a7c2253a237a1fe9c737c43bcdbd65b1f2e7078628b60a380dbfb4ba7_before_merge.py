    def from_dict(self, dct, cls=None, schema=None, rootschema=None):
        """Construct an object from a dict representation"""
        if (schema is None) == (cls is None):
            raise ValueError("Must provide either cls or schema, but not both.")
        if schema is None:
            schema = schema or cls._schema
            rootschema = rootschema or cls._rootschema
        rootschema = rootschema or schema

        def _passthrough(*args, **kwds):
            return args[0] if args else kwds

        if cls is None:
            # TODO: do something more than simply selecting the last match?
            matches = self.class_dict[self.hash_schema(schema)]
            cls = matches[-1] if matches else _passthrough
        schema = _resolve_references(schema, rootschema)

        if 'anyOf' in schema or 'oneOf' in schema:
            schemas = schema.get('anyOf', []) + schema.get('oneOf', [])
            for possible_schema in schemas:
                resolver = jsonschema.RefResolver.from_schema(rootschema)
                try:
                    jsonschema.validate(dct, possible_schema, resolver=resolver)
                except jsonschema.ValidationError:
                    continue
                else:
                    return self.from_dict(dct,
                        schema=possible_schema,
                        rootschema=rootschema,
                    )

        if isinstance(dct, dict):
            # TODO: handle schemas for additionalProperties/patternProperties
            props = schema.get('properties', {})
            kwds = {}
            for key, val in dct.items():
                if key in props:
                    val = self.from_dict(val,
                        schema=props[key],
                        rootschema=rootschema
                    )
                kwds[key] = val
            return cls(**kwds)

        elif isinstance(dct, list):
            item_schema = schema.get('items', {})
            dct = [self.from_dict(val,
                       schema=item_schema,
                       rootschema=rootschema
                   ) for val in dct]
            return cls(dct)
        else:
            return cls(dct)