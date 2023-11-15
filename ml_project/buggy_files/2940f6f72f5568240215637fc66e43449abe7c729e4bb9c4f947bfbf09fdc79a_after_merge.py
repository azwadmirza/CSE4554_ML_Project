    def analyze_types(self, types: List[Type], node: Node) -> None:
        # Similar to above but for nodes with multiple types.
        indicator = {}  # type: Dict[str, bool]
        for type in types:
            analyzer = self.make_type_analyzer(indicator)
            type.accept(analyzer)
            self.check_for_omitted_generics(type)
        if indicator.get('forward') or indicator.get('synthetic'):
            def patch() -> None:
                self.perform_transform(node,
                    lambda tp: tp.accept(ForwardReferenceResolver(self.fail,
                                                                  node, warn=False)))
            self.patches.append(patch)