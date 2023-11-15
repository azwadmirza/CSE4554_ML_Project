    def visit_desc_annotation(self, node: Element) -> None:
        # Try to avoid duplicating info already displayed by the deffn category.
        # e.g.
        #     @deffn {Class} Foo
        #     -- instead of --
        #     @deffn {Class} class Foo
        txt = node.astext().strip()
        if txt == self.desc['desctype'] or \
           txt == self.desc['objtype'] or \
           txt in self.desc_type_name.split():
            raise nodes.SkipNode