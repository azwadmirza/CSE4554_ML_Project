    def visit_desc(self, node: Element) -> None:
        self.desc = node
        self.at_deffnx = '@deffn'