    def replace(self, other):
        for x in self:
            replace_hy_obj(x, other)

        HyObject.replace(self, other)
        return self