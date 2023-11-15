    def validate(self):
        super(Rolling, self).validate()
        if not com.is_integer(self.window):
            raise ValueError("window must be an integer")