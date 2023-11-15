    def validate(self, value):
        return compat.intern(str(super(Identifier, self).validate(value)))