    def persistent_parse_hypermap(self, index=0, downsample=None,
                                  cutoff_at_kV=None,
                                  lazy=False):
        """Parse and assign the hypermap to the HyperMap instance.

        Arguments:
        index -- index of hypermap in bcf if v2 (default 0)
        downsample -- downsampling factor of hypermap (default None)
        cutoff_at_kV -- low pass cutoff value at keV (default None)

        Method does not return anything, it adds the HyperMap instance to
        self.hypermap dictionary.

        See also:
        HyperMap, parse_hypermap
        """
        dwn = downsample
        hypermap = self.parse_hypermap(index=index,
                                       downsample=dwn,
                                       cutoff_at_kV=cutoff_at_kV,
                                       lazy=lazy)
        self.hypermap[index] = HyperMap(hypermap,
                                        self,
                                        index=index,
                                        downsample=dwn)