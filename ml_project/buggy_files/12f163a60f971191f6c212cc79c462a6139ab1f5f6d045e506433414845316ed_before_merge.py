    def edge_width(self, edge_width: Union[None, float]) -> None:
        self._edge_width = edge_width
        self.status = format_float(self.edge_width)
        self.events.edge_width()
        self.events.highlight()