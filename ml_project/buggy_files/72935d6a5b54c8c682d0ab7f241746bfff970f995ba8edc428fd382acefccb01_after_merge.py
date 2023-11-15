    def active_self_type(self) -> Optional[Union[Instance, TupleType]]:
        """An instance or tuple type representing the current class.

        This returns None unless we are in class body or in a method.
        In particular, inside a function nested in method this returns None.
        """
        info = self.active_class()
        if not info and self.top_function():
            info = self.enclosing_class()
        if info:
            return fill_typevars(info)
        return None