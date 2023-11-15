    def anal_type(self, tp: UnboundType) -> Type:
        tpan = TypeAnalyser(self.lookup_func,
                            self.lookup_fqn_func,
                            None,
                            self.fail,
                            self.note_func,
                            self.plugin,
                            self.options,
                            self.is_typeshed_stub,
                            third_pass=True)
        return tp.accept(tpan)