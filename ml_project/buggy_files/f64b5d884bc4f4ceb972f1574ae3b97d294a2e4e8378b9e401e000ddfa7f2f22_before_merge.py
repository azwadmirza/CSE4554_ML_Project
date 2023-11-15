    def replace(self, other):
        if self.car is not None:
            replace_hy_obj(self.car, other)
        if self.cdr is not None:
            replace_hy_obj(self.cdr, other)

        HyObject.replace(self, other)