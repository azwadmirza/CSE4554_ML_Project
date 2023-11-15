    def string_references(self, minimum_length=2, vex_only=False):
        """
        All of the constant string references used by this function.

        :param minimum_length:  The minimum length of strings to find (default is 1)
        :param vex_only:        Only analyze VEX IR, don't interpret the entry state to detect additional constants.
        :return:                A list of tuples of (address, string) where is address is the location of the string in
                                memory.
        """
        strings = []
        memory = self._project.loader.memory

        # get known instruction addresses and call targets
        # these addresses cannot be string references, but show up frequently in the runtime values
        known_executable_addresses = set()
        for block in self.blocks:
            known_executable_addresses.update(block.instruction_addrs)
        for function in self._function_manager.values():
            known_executable_addresses.update(set(x.addr for x in function.graph.nodes()))

        # loop over all local runtime values and check if the value points to a printable string
        for addr in self.local_runtime_values if not vex_only else self.code_constants:
            if not isinstance(addr, claripy.fp.FPV) and addr in memory:
                # check that the address isn't an pointing to known executable code
                # and that it isn't an indirect pointer to known executable code
                try:
                    possible_pointer = memory.unpack_word(addr)
                    if addr not in known_executable_addresses and possible_pointer not in known_executable_addresses:
                        # build string
                        stn = ""
                        offset = 0
                        current_char = chr(memory[addr + offset])
                        while current_char in string.printable:
                            stn += current_char
                            offset += 1
                            current_char = chr(memory[addr + offset])

                        # check that the string was a null terminated string with minimum length
                        if current_char == "\x00" and len(stn) >= minimum_length:
                            strings.append((addr, stn))
                except KeyError:
                    pass
        return strings