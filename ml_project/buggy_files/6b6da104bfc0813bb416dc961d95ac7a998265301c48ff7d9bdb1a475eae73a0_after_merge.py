    def add_fignumber(self, node):
        def append_fignumber(figtype, figure_id):
            if figure_id in self.builder.fignumbers.get(figtype, {}):
                self.body.append(self.starttag(node, 'span', '', CLASS='caption-number'))
                prefix = self.builder.config.numfig_prefix.get(figtype, '')
                numbers = self.builder.fignumbers[figtype][figure_id]
                self.body.append(prefix + '.'.join(map(str, numbers)) + " ")
                self.body.append('</span>')

        if isinstance(node.parent, nodes.figure):
            append_fignumber('figure', node.parent['ids'][0])
        elif isinstance(node.parent, nodes.table):
            append_fignumber('table', node.parent['ids'][0])
        elif isinstance(node.parent, nodes.container):
            append_fignumber('code-block', node.parent['ids'][0])