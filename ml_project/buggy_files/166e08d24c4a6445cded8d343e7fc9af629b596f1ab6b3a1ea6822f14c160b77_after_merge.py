    def _next_code_addr_core(self):
        """
        Call _next_unscanned_addr() first to get the next address that is not scanned. Then check if data locates at
        that address seems to be code or not. If not, we'll continue to for the next un-scanned address.
        """

        next_addr = self._next_unscanned_addr()
        if next_addr is None:
            return None

        start_addr = next_addr

        while True:
            string_length = self._scan_for_printable_strings(start_addr)
            if string_length:
                self._seg_list.occupy(start_addr, string_length, "string")
                start_addr += string_length

            if self.project.arch.name in ('X86', 'AMD64'):
                cc_length = self._scan_for_repeating_bytes(start_addr, 0xcc, threshold=1)
                if cc_length:
                    self._seg_list.occupy(start_addr, cc_length, "alignment")
                    start_addr += cc_length
            else:
                cc_length = 0

            zeros_length = self._scan_for_repeating_bytes(start_addr, 0x00)
            if zeros_length:
                self._seg_list.occupy(start_addr, zeros_length, "alignment")
                start_addr += zeros_length

            if string_length == 0 and cc_length == 0 and zeros_length == 0:
                # umm now it's probably code
                break

        instr_alignment = self._initial_state.arch.instruction_alignment
        if start_addr % instr_alignment > 0:
            # occupy those few bytes
            self._seg_list.occupy(start_addr, instr_alignment - (start_addr % instr_alignment), 'alignment')
            start_addr = start_addr - start_addr % instr_alignment + \
                         instr_alignment
            # trickiness: aligning the start_addr may create a new address that is outside any mapped region.
            if not self._inside_regions(start_addr):
                raise ContinueScanningNotification()

        return start_addr