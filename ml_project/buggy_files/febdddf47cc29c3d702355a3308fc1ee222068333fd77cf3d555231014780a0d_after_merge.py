    def __repr__(self):
        ret = super(UnifiedResponse, self).__repr__()
        ret += '\n' + str(self)

        return ret