    def depart_desc(self, node: Element) -> None:
        self.desc = None
        self.ensure_eol()
        self.body.append('@end deffn\n')