    def unify(self):
        """
        Run the final unification pass over all inferred types, and
        catch imprecise types.
        """
        typdict = utils.UniqueDict()

        def find_offender(name, exhaustive=False):
            # finds the offending variable definition by name
            # if exhaustive is set it will try and trace through temporary
            # variables to find a concrete offending definition.
            offender = None
            for block in self.func_ir.blocks.values():
                offender = block.find_variable_assignment(name)
                if offender is not None:
                    if not exhaustive:
                        break
                    try: # simple assignment
                        hasattr(offender.value, 'name')
                        offender_value = offender.value.name
                    except (AttributeError, KeyError):
                        break
                    orig_offender = offender
                    if offender_value.startswith('$'):
                        offender = find_offender(offender_value,
                                                 exhaustive=exhaustive)
                        if offender is None:
                            offender = orig_offender
                    break
            return offender

        def diagnose_imprecision(offender):
            # helper for diagnosing imprecise types

            list_msg = """\n
For Numba to be able to compile a list, the list must have a known and
precise type that can be inferred from the other variables. Whilst sometimes
the type of empty lists can be inferred, this is not always the case, see this
documentation for help:

http://numba.pydata.org/numba-doc/latest/user/troubleshoot.html#my-code-has-an-untyped-list-problem
"""
            if offender is not None:
                # This block deals with imprecise lists
                if hasattr(offender, 'value'):
                    if hasattr(offender.value, 'op'):
                        # might be `foo = []`
                        if offender.value.op == 'build_list':
                            return list_msg
                        # or might be `foo = list()`
                        elif offender.value.op == 'call':
                            try: # assignment involving a call
                                call_name = offender.value.func.name
                                # find the offender based on the call name
                                offender = find_offender(call_name)
                                if isinstance(offender.value, ir.Global):
                                    if offender.value.name == 'list':
                                        return list_msg
                            except (AttributeError, KeyError):
                                pass
            return "" # no help possible

        def check_var(name):
            tv = self.typevars[name]
            if not tv.defined:
                offender = find_offender(name)
                val = getattr(offender, 'value', 'unknown operation')
                loc = getattr(offender, 'loc', ir.unknown_loc)
                msg = "Undefined variable '%s', operation: %s, location: %s"
                raise TypingError(msg % (var, val, loc), loc)
            tp = tv.getone()
            if not tp.is_precise():
                offender = find_offender(name, exhaustive=True)
                msg = ("Cannot infer the type of variable '%s'%s, "
                      "have imprecise type: %s. %s")
                istmp = " (temporary variable)" if var.startswith('$') else ""
                loc = getattr(offender, 'loc', ir.unknown_loc)
                # is this an untyped list? try and provide help
                extra_msg = diagnose_imprecision(offender)
                raise TypingError(msg % (var, istmp, tp, extra_msg), loc)
            else: # type is precise, hold it
                typdict[var] = tp

        # For better error display, check first user-visible vars, then
        # temporaries
        temps = set(k for k in self.typevars if not k[0].isalpha())
        others = set(self.typevars) - temps
        for var in sorted(others):
            check_var(var)
        for var in sorted(temps):
            check_var(var)

        retty = self.get_return_type(typdict)
        fntys = self.get_function_types(typdict)
        if self.generator_info:
            retty = self.get_generator_type(typdict, retty)

        self.debug.unify_finished(typdict, retty, fntys)

        return typdict, retty, fntys