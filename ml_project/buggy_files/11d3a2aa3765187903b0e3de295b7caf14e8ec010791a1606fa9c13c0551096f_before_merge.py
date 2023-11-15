    def from_obj(self, value):
        if value is None:
            return {}

        return {self.keytype.from_obj(key): self.valtype.from_obj(val)
                for key, val in value.items()}