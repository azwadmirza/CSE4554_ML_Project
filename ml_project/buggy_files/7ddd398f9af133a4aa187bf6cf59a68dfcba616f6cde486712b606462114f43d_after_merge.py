    def append(self, pane):
        from .pane import panel
        name = None
        if isinstance(pane, tuple):
            name, pane = pane
        new_objects = list(self)
        new_objects.append(panel(pane, name=name))
        name = param_name(new_objects[-1].name) if name is None else name
        self._names.append(name)
        self.objects = new_objects