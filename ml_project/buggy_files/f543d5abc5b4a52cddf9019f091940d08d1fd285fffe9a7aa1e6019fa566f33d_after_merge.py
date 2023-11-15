    def _deactivate(self):
        if self._gtype in (gl.GL_SAMPLER_2D, GL_SAMPLER_3D):
            #gl.glActiveTexture(gl.GL_TEXTURE0 + self._unit)
            if self.data is not None:
                if isinstance(self._data, BaseTexture):
                    self.data.deactivate()