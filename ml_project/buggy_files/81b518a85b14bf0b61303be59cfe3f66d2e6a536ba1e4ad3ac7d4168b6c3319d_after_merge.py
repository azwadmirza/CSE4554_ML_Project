    def make_xref(self, rolename, domain, target, innernode=nodes.emphasis,
                  contnode=None):
        result = super(PyXrefMixin, self).make_xref(rolename, domain, target,
                                                    innernode, contnode)
        result['refspecific'] = True
        if target.startswith(('.', '~')):
            prefix, result['reftarget'] = target[0], target[1:]
            if prefix == '.':
                text = target[1:]
            elif prefix == '~':
                text = target.split('.')[-1]
            for node in result.traverse(nodes.Text):
                node.parent[node.parent.index(node)] = nodes.Text(text)
                break
        return result