    def visit_caption(self, node):
        if isinstance(node.parent, nodes.container) and node.parent.get('literal_block'):
            self.body.append(self.starttag(node, 'div', '', CLASS='code-block-caption'))
        else:
            BaseTranslator.visit_caption(self, node)
        self.add_fignumber(node)
        self.body.append(self.starttag(node, 'span', '', CLASS='caption-text'))