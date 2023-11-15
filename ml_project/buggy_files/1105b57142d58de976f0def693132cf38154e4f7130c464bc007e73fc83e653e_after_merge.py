    def create_as(self, type: Type[T], id: str) -> T:
        """
        Create a new model element of type 'type' with 'id' as its ID.
        This method should only be used when loading models, since it does
        not emit an ElementCreated event.
        """
        if not type or not issubclass(type, Element) or issubclass(type, Presentation):
            raise TypeError(f"Type {type} is not a valid model element")
        obj = type(id, self)
        self._elements[id] = obj
        return obj