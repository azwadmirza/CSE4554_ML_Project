    def __repr__(self):
        if PRETTY:
            return str(self)
        else:
            return "HyCons({}, {})".format(
                repr(self.car), repr(self.cdr))