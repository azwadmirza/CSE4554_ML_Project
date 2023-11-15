    def instruction_size(self, insn_addr):
        """
        Get the size of the instruction specified by `insn_addr`.

        :param int insn_addr: Address of the instruction
        :return int: Size of the instruction in bytes, or None if the instruction is not found.
        """

        for b in self.blocks:
            block = self.get_block(b.addr, size=b.size, byte_string=b.bytestr)
            if insn_addr in block.instruction_addrs:
                index = block.instruction_addrs.index(insn_addr)
                if index == len(block.instruction_addrs) - 1:
                    # the very last instruction
                    size = block.addr + block.size - insn_addr
                else:
                    size = block.instruction_addrs[index + 1] - insn_addr
                return size

        return None