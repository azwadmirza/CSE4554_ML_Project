    def active_self_type(self) -> Optional[Union[Instance, TupleType]]:
        info = self.active_class()
        if info:
            return fill_typevars(info)
        return None