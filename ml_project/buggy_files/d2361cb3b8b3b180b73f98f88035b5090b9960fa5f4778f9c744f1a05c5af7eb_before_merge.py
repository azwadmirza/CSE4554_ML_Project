    def get_instructions(self, f, bb):
        for insn in capa.features.extractors.ida.helpers.get_instructions_in_range(bb.start_ea, bb.end_ea):
            yield add_va_int_cast(insn)