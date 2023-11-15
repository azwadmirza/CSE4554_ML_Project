    def analyze(self, type: Optional[Type], node: Union[Node, SymbolTableNode],
                warn: bool = False) -> None:
        # Recursive type warnings are only emitted on type definition 'node's, marked by 'warn'
        # Flags appeared during analysis of 'type' are collected in this dict.
        indicator = {}  # type: Dict[str, bool]
        if type:
            analyzer = self.make_type_analyzer(indicator)
            type.accept(analyzer)
            self.check_for_omitted_generics(type)
            if indicator.get('forward') or indicator.get('synthetic'):
                def patch() -> None:
                    self.perform_transform(node,
                        lambda tp: tp.accept(ForwardReferenceResolver(self.fail,
                                                                      node, warn)))
                self.patches.append(patch)