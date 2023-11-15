    def depart_desc(self, node: addnodes.desc) -> None:
        self.descs.pop()
        self.ensure_eol()
        self.body.append('@end deffn\n')