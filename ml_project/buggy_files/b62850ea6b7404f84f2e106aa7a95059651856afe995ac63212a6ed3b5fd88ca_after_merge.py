    def create_as(self, type, id, parent=None, subject=None):
        if not type or not issubclass(type, gaphas.Item):
            raise TypeError(
                f"Type {type} can not be added to a diagram as it is not a diagram item"
            )
        item = type(id, self.model)
        if subject:
            item.subject = subject
        self.canvas.add(item, parent)
        self.model.handle(DiagramItemCreated(self.model, item))
        return item