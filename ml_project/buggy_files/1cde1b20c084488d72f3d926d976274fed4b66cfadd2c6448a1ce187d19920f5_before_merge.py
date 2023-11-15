    def is_type_obj(self) -> bool:
        t = self.fallback.type
        return t is not None and t.is_metaclass()