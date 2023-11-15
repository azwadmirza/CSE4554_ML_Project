    def check_simple_str_interpolation(self, specifiers: List[ConversionSpecifier],
                                       replacements: Expression) -> None:
        checkers = self.build_replacement_checkers(specifiers, replacements)
        if checkers is None:
            return

        rhs_type = self.accept(replacements)
        rep_types = []  # type: List[Type]
        if isinstance(rhs_type, TupleType):
            rep_types = rhs_type.items
        elif isinstance(rhs_type, AnyType):
            return
        else:
            rep_types = [rhs_type]

        if len(checkers) > len(rep_types):
            self.msg.too_few_string_formatting_arguments(replacements)
        elif len(checkers) < len(rep_types):
            self.msg.too_many_string_formatting_arguments(replacements)
        else:
            if len(checkers) == 1:
                check_node, check_type = checkers[0]
                if isinstance(rhs_type, TupleType) and len(rhs_type.items) == 1:
                    check_type(rhs_type.items[0])
                else:
                    check_node(replacements)
            elif (isinstance(replacements, TupleExpr)
                  and not any(isinstance(item, StarExpr) for item in replacements.items)):
                for checks, rep_node in zip(checkers, replacements.items):
                    check_node, check_type = checks
                    check_node(rep_node)
            else:
                for checks, rep_type in zip(checkers, rep_types):
                    check_node, check_type = checks
                    check_type(rep_type)