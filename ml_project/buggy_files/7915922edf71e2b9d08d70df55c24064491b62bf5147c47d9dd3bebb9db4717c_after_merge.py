    def getLookupTable(self, start=0.0, stop=1.0, nPts=512, alpha=None, mode='byte'):
        """
        Return an RGB(A) lookup table (ndarray). 
        
        ===============   =============================================================================
        **Arguments:**
        start             The starting value in the lookup table (default=0.0)
        stop              The final value in the lookup table (default=1.0)
        nPts              The number of points in the returned lookup table.
        alpha             True, False, or None - Specifies whether or not alpha values are included
                          in the table. If alpha is None, it will be automatically determined.
        mode              Determines return type: 'byte' (0-255), 'float' (0.0-1.0), or 'qcolor'.
                          See :func:`map() <pyqtgraph.ColorMap.map>`.
        ===============   =============================================================================
        """
        if isinstance(mode, basestring):
            mode = self.enumMap[mode.lower()]
        
        if alpha is None:
            alpha = self.usesAlpha()
            
        x = np.linspace(start, stop, nPts)
        table = self.map(x, mode)
        
        if not alpha and mode != self.QCOLOR:
            return table[:,:3]
        else:
            return table