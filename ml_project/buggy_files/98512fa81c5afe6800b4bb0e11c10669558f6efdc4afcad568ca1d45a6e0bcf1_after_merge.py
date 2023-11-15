    def visit_title(self, node):
        BaseTranslator.visit_title(self, node)
        self.add_secnumber(node)
        self.add_fignumber(node)
        if isinstance(node.parent, nodes.table):
            self.body.append(self.starttag(node, 'span', '', CLASS='caption-text'))