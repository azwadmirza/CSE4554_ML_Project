    def is_type_obj(self) -> bool:
        return self.fallback.type.is_metaclass()