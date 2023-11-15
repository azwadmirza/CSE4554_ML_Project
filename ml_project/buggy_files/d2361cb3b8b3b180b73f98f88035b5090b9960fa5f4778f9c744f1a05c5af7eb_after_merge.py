    def get_instructions(self, f, bb):
        import capa.features.extractors.ida.helpers as ida_helpers
        for insn in ida_helpers.get_instructions_in_range(bb.start_ea, bb.end_ea):
            yield add_va_int_cast(insn)