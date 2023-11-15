    def visit_instance(self, template: Instance) -> List[Constraint]:
        original_actual = actual = self.actual
        res = []  # type: List[Constraint]
        if isinstance(actual, (CallableType, Overloaded)) and template.type.is_protocol:
            if template.type.protocol_members == ['__call__']:
                # Special case: a generic callback protocol
                if not any(mypy.sametypes.is_same_type(template, t)
                           for t in template.type.inferring):
                    template.type.inferring.append(template)
                    call = mypy.subtypes.find_member('__call__', template, actual,
                                                     is_operator=True)
                    assert call is not None
                    if mypy.subtypes.is_subtype(actual, erase_typevars(call)):
                        subres = infer_constraints(call, actual, self.direction)
                        res.extend(subres)
                    template.type.inferring.pop()
                    return res
        if isinstance(actual, CallableType) and actual.fallback is not None:
            actual = actual.fallback
        if isinstance(actual, Overloaded) and actual.fallback is not None:
            actual = actual.fallback
        if isinstance(actual, TypedDictType):
            actual = actual.as_anonymous().fallback
        if isinstance(actual, LiteralType):
            actual = actual.fallback
        if isinstance(actual, Instance):
            instance = actual
            erased = erase_typevars(template)
            assert isinstance(erased, Instance)  # type: ignore
            # We always try nominal inference if possible,
            # it is much faster than the structural one.
            if (self.direction == SUBTYPE_OF and
                    template.type.has_base(instance.type.fullname)):
                mapped = map_instance_to_supertype(template, instance.type)
                tvars = mapped.type.defn.type_vars
                for i in range(len(instance.args)):
                    # The constraints for generic type parameters depend on variance.
                    # Include constraints from both directions if invariant.
                    if tvars[i].variance != CONTRAVARIANT:
                        res.extend(infer_constraints(
                            mapped.args[i], instance.args[i], self.direction))
                    if tvars[i].variance != COVARIANT:
                        res.extend(infer_constraints(
                            mapped.args[i], instance.args[i], neg_op(self.direction)))
                return res
            elif (self.direction == SUPERTYPE_OF and
                    instance.type.has_base(template.type.fullname)):
                mapped = map_instance_to_supertype(instance, template.type)
                tvars = template.type.defn.type_vars
                for j in range(len(template.args)):
                    # The constraints for generic type parameters depend on variance.
                    # Include constraints from both directions if invariant.
                    if tvars[j].variance != CONTRAVARIANT:
                        res.extend(infer_constraints(
                            template.args[j], mapped.args[j], self.direction))
                    if tvars[j].variance != COVARIANT:
                        res.extend(infer_constraints(
                            template.args[j], mapped.args[j], neg_op(self.direction)))
                return res
            if (template.type.is_protocol and self.direction == SUPERTYPE_OF and
                    # We avoid infinite recursion for structural subtypes by checking
                    # whether this type already appeared in the inference chain.
                    # This is a conservative way break the inference cycles.
                    # It never produces any "false" constraints but gives up soon
                    # on purely structural inference cycles, see #3829.
                    # Note that we use is_protocol_implementation instead of is_subtype
                    # because some type may be considered a subtype of a protocol
                    # due to _promote, but still not implement the protocol.
                    not any(mypy.sametypes.is_same_type(template, t)
                            for t in template.type.inferring) and
                    mypy.subtypes.is_protocol_implementation(instance, erased)):
                template.type.inferring.append(template)
                self.infer_constraints_from_protocol_members(res, instance, template,
                                                             original_actual, template)
                template.type.inferring.pop()
                return res
            elif (instance.type.is_protocol and self.direction == SUBTYPE_OF and
                  # We avoid infinite recursion for structural subtypes also here.
                  not any(mypy.sametypes.is_same_type(instance, i)
                          for i in instance.type.inferring) and
                  mypy.subtypes.is_protocol_implementation(erased, instance)):
                instance.type.inferring.append(instance)
                self.infer_constraints_from_protocol_members(res, instance, template,
                                                             template, instance)
                instance.type.inferring.pop()
                return res
        if isinstance(actual, AnyType):
            # IDEA: Include both ways, i.e. add negation as well?
            return self.infer_against_any(template.args, actual)
        if (isinstance(actual, TupleType) and
            (is_named_instance(template, 'typing.Iterable') or
             is_named_instance(template, 'typing.Container') or
             is_named_instance(template, 'typing.Sequence') or
             is_named_instance(template, 'typing.Reversible'))
                and self.direction == SUPERTYPE_OF):
            for item in actual.items:
                cb = infer_constraints(template.args[0], item, SUPERTYPE_OF)
                res.extend(cb)
            return res
        elif isinstance(actual, TupleType) and self.direction == SUPERTYPE_OF:
            return infer_constraints(template,
                                     mypy.typeops.tuple_fallback(actual),
                                     self.direction)
        else:
            return []