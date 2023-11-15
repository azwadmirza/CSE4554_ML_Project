    def analyze(self, type: Optional[Type], node: Union[Node, SymbolTableNode],
                warn: bool = False) -> None:
        # Recursive type warnings are only emitted on type definition 'node's, marked by 'warn'
        # Flags appeared during analysis of 'type' are collected in this dict.
        indicator = {}  # type: Dict[str, bool]
        if type:
            analyzer = self.make_type_analyzer(indicator)
            type.accept(analyzer)
            self.check_for_omitted_generics(type)
            self.generate_type_patches(node, indicator, warn)