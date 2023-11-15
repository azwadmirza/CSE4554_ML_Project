    def visit_target(self, node):
        # postpone the labels until after the sectioning command
        parindex = node.parent.index(node)
        try:
            try:
                next = node.parent[parindex+1]
            except IndexError:
                # last node in parent, look at next after parent
                # (for section of equal level)
                next = node.parent.parent[node.parent.parent.index(node.parent)]
            if isinstance(next, nodes.section):
                if node.get('refid'):
                    self.next_section_ids.add(node['refid'])
                self.next_section_ids.update(node['ids'])
                return
        except (IndexError, AttributeError):
            pass
        if 'refuri' in node:
            return
        if node.get('refid'):
            self.add_anchor(node['refid'], node)
        for id in node['ids']:
            self.add_anchor(id, node)