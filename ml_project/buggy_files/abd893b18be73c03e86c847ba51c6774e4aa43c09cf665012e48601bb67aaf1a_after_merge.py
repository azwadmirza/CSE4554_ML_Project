    def check_multi_assignment_from_tuple(self, lvalues: List[Lvalue], rvalue: Expression,
                                          rvalue_type: TupleType, context: Context,
                                          undefined_rvalue: bool,
                                          infer_lvalue_type: bool = True) -> None:
        if self.check_rvalue_count_in_assignment(lvalues, len(rvalue_type.items), context):
            star_index = next((i for i, lv in enumerate(lvalues)
                               if isinstance(lv, StarExpr)), len(lvalues))

            left_lvs = lvalues[:star_index]
            star_lv = cast(StarExpr, lvalues[star_index]) if star_index != len(lvalues) else None
            right_lvs = lvalues[star_index + 1:]

            if not undefined_rvalue:
                # Infer rvalue again, now in the correct type context.
                lvalue_type = self.lvalue_type_for_inference(lvalues, rvalue_type)
                reinferred_rvalue_type = self.expr_checker.accept(rvalue, lvalue_type)

                if isinstance(reinferred_rvalue_type, UnionType):
                    # If this is an Optional type in non-strict Optional code, unwrap it.
                    relevant_items = reinferred_rvalue_type.relevant_items()
                    if len(relevant_items) == 1:
                        reinferred_rvalue_type = relevant_items[0]
                if isinstance(reinferred_rvalue_type, UnionType):
                    self.check_multi_assignment_from_union(lvalues, rvalue,
                                                           reinferred_rvalue_type, context,
                                                           infer_lvalue_type)
                    return
                assert isinstance(reinferred_rvalue_type, TupleType)
                rvalue_type = reinferred_rvalue_type

            left_rv_types, star_rv_types, right_rv_types = self.split_around_star(
                rvalue_type.items, star_index, len(lvalues))

            for lv, rv_type in zip(left_lvs, left_rv_types):
                self.check_assignment(lv, self.temp_node(rv_type, context), infer_lvalue_type)
            if star_lv:
                list_expr = ListExpr([self.temp_node(rv_type, context)
                                      for rv_type in star_rv_types])
                list_expr.set_line(context.get_line())
                self.check_assignment(star_lv.expr, list_expr, infer_lvalue_type)
            for lv, rv_type in zip(right_lvs, right_rv_types):
                self.check_assignment(lv, self.temp_node(rv_type, context), infer_lvalue_type)