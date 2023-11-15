    def analyze_property_with_multi_part_definition(self, defn: OverloadedFuncDef) -> None:
        """Analyze a property defined using multiple methods (e.g., using @x.setter).

        Assume that the first method (@property) has already been analyzed.
        """
        defn.is_property = True
        items = defn.items
        first_item = cast(Decorator, defn.items[0])
        for item in items[1:]:
            if isinstance(item, Decorator) and len(item.decorators) == 1:
                node = item.decorators[0]
                if isinstance(node, MemberExpr):
                    if node.name == 'setter':
                        # The first item represents the entire property.
                        first_item.var.is_settable_property = True
                        # Get abstractness from the original definition.
                        item.func.is_abstract = first_item.func.is_abstract
                item.func.accept(self)
            else:
                self.fail("Decorated property not supported", item)