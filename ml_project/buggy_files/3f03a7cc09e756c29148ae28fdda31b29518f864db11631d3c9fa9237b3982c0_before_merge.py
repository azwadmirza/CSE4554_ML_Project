    def _repr_html_(self):
        ret = ''
        for block in self.responses:
            ret += "Results from the {}:\n".format(block.client.__class__.__name__)
            ret += block._repr_html_()
            ret += '\n'

        return ret