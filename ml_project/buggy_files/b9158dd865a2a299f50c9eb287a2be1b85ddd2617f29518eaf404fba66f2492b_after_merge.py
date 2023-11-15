    def validate(self, value):
        value = super(Identifier, self).validate(value)
        if isinstance(value, compat.text_type):
            value = value.encode('utf-8')
        return compat.intern(value)