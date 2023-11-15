    def prepare_target(self, operation, address=None, clock=0, reset=True):
        """!
        This function sets up target clocks to ensure that flash is clocked at the maximum
        of 24MHz. Doing so gets the best flash programming performance. The FIRC clock source
        is used so that there is no dependency on an external crystal frequency.
        """
        super(Flash_kl28z, self).init(operation, address, clock, reset)

        # Enable FIRC.
        value = self.target.read32(SCG_FIRCCSR)
        self._saved_firccsr = value
        value |= FIRCEN_MASK
        self.target.write32(SCG_FIRCCSR, value)

        # Switch system to FIRC, core=48MHz (/1), slow=24MHz (/2).
        # Flash and the bus are clocked from the slow clock, and its max is 24MHz,
        # so there is no benefit from raising the core clock further.
        self._saved_rccr = self.target.read32(SCG_RCCR)
        self.target.write32(SCG_RCCR, (0x3 << SCS_SHIFT) | (1 << DIVSLOW_SHIFT))

        csr = self.target.read32(SCG_CSR)
        LOG.debug("SCG_CSR = 0x%08x", csr)