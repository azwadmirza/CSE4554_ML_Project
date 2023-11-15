    def _init(self):
        if True:  # not self._initialized:
            if not self.Q._initialized:
                self.Q._init()
            self._set_transform()
            _pivot = self.Q.pivot
            self.Q.pivot = self.pivot[self.labelpos]
            # Hack: save and restore the Umask
            _mask = self.Q.Umask
            self.Q.Umask = ma.nomask
            self.verts = self.Q._make_verts(np.array([self.U]),
                                            np.zeros((1,)))
            self.Q.Umask = _mask
            self.Q.pivot = _pivot
            kw = self.Q.polykw
            kw.update(self.kw)
            self.vector = mcollections.PolyCollection(
                                        self.verts,
                                        offsets=[(self.X, self.Y)],
                                        transOffset=self.get_transform(),
                                        **kw)
            if self.color is not None:
                self.vector.set_color(self.color)
            self.vector.set_transform(self.Q.get_transform())
            self.vector.set_figure(self.get_figure())
            self._initialized = True