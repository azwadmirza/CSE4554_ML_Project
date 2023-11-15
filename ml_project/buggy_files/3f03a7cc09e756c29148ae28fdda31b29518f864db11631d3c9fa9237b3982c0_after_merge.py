    def _repr_html_(self):
        nprov = len(self)
        if nprov == 1:
            ret = 'Results from {} Provider:</br></br>'.format(len(self))
        else:
            ret = 'Results from {} Providers:</br></br>'.format(len(self))
        for block in self.responses:
            ret += "{} Results from the {}:</br>".format(len(block), block.client.__class__.__name__)
            ret += block._repr_html_()
            ret += '</br>'

        return ret