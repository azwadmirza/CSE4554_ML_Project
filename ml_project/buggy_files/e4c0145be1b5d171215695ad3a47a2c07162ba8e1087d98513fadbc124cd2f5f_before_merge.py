    def __str__(self):
        cls = self.obj.__class__
        schema_path = ['{}.{}'.format(cls.__module__, cls.__name__)]
        schema_path.extend(self.schema_path)
        schema_path = '->'.join(val for val in schema_path[:-1]
                                if val not in ('properties',
                                               'additionalProperties',
                                               'patternProperties'))
        return """Invalid specification

        {}, validating {!r}

        {}
        """.format(schema_path, self.validator, self.message)