    def make_xref(self, rolename, domain, target, innernode=nodes.emphasis,
                  contnode=None):
        result = super(PyXrefMixin, self).make_xref(rolename, domain, target,
                                                    innernode, contnode)
        result['refspecific'] = True
        if target.startswith('.'):
            result['reftarget'] = target[1:]
            result[0][0] = nodes.Text(target[1:])
        if target.startswith('~'):
            result['reftarget'] = target[1:]
            title = target.split('.')[-1]
            result[0][0] = nodes.Text(title)
        return result