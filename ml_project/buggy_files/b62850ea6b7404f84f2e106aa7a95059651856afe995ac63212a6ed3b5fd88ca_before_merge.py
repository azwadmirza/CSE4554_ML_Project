    def create_as(self, type, id, parent=None, subject=None):
        item = type(id, self.model)
        if subject:
            item.subject = subject
        self.canvas.add(item, parent)
        self.model.handle(DiagramItemCreated(self.model, item))
        return item