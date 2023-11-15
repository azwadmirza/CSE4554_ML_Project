    def depthIncCheck(self):
        """
        Check that no slowness layer is too thick.

        The maximum is determined by ``self.maxDepthInterval``.
        """
        for wave in [self.SWAVE, self.PWAVE]:
            # These might change with calls to addSlowness, so be sure we have
            # the correct copy.
            if wave == self.PWAVE:
                layers = self.PLayers
            else:
                layers = self.SLayers

            diff = layers['botDepth'] - layers['topDepth']

            mask = diff > self.maxDepthInterval
            diff = diff[mask]
            topDepth = layers['topDepth'][mask]

            new_count = np.ceil(diff / self.maxDepthInterval).astype(np.int_)
            steps = diff / new_count

            for start, Nd, delta in zip(topDepth, new_count, steps):
                new_depth = start + np.arange(1, Nd) * delta
                if wave == self.SWAVE:
                    velocity = self.vMod.evaluateAbove(new_depth, 'S')

                    smask = velocity == 0
                    if not self.allowInnerCoreS:
                        smask |= new_depth >= self.vMod.iocbDepth
                    velocity[smask] = self.vMod.evaluateAbove(new_depth[smask],
                                                              'P')

                    slowness = self.toSlowness(velocity, new_depth)
                else:
                    slowness = self.toSlowness(
                        self.vMod.evaluateAbove(new_depth, 'P'),
                        new_depth)

                for p in slowness:
                    self.addSlowness(p, self.PWAVE)
                    self.addSlowness(p, self.SWAVE)