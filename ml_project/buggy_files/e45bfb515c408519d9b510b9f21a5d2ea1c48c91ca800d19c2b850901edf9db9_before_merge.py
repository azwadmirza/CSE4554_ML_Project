    def clim(self, clim):
        self._clim_msg = f'{clim[0]: 0.3}, {clim[1]: 0.3}'
        self.status = self._clim_msg
        self._node.clim = clim
        self.events.clim()