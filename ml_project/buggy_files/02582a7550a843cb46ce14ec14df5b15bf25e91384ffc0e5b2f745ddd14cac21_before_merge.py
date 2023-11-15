    def visit_callable_type(self, template: CallableType) -> List[Constraint]:
        if isinstance(self.actual, CallableType):
            cactual = self.actual
            # FIX verify argument counts
            # FIX what if one of the functions is generic
            res = []  # type: List[Constraint]

            # We can't infer constraints from arguments if the template is Callable[..., T] (with
            # literal '...').
            if not template.is_ellipsis_args:
                # The lengths should match, but don't crash (it will error elsewhere).
                for t, a in zip(template.arg_types, cactual.arg_types):
                    # Negate direction due to function argument type contravariance.
                    res.extend(infer_constraints(t, a, neg_op(self.direction)))
            res.extend(infer_constraints(template.ret_type, cactual.ret_type,
                                         self.direction))
            return res
        elif isinstance(self.actual, AnyType):
            # FIX what if generic
            res = self.infer_against_any(template.arg_types, self.actual)
            any_type = AnyType(TypeOfAny.from_another_any, source_any=self.actual)
            res.extend(infer_constraints(template.ret_type, any_type, self.direction))
            return res
        elif isinstance(self.actual, Overloaded):
            return self.infer_against_overloaded(self.actual, template)
        elif isinstance(self.actual, TypeType):
            return infer_constraints(template.ret_type, self.actual.item, self.direction)
        elif isinstance(self.actual, Instance):
            # Instances with __call__ method defined are considered structural
            # subtypes of Callable with a compatible signature.
            call = mypy.subtypes.find_member('__call__', self.actual, self.actual)
            if call:
                return infer_constraints(template, call, self.direction)
            else:
                return []
        else:
            return []