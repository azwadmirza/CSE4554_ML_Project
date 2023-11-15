    def visit_desc(self, node: addnodes.desc) -> None:
        self.descs.append(node)
        self.at_deffnx = '@deffn'