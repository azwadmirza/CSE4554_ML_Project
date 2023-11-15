    def to_coils(self):
        """Convert the payload buffer into a coil
        layout that can be used as a context block.

        :returns: The coil layout to use as a block
        """
        payload = self.to_registers()
        coils = [bool(int(bit)) for reg
                 in payload for bit in format(reg, '016b')]
        return coils