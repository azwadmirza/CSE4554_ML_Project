    def _unify_return_types(self, rettypes):
        if rettypes:
            unified = self.context.unify_types(*rettypes)
            if unified is None or not unified.is_precise():
                def check_type(atype):
                    lst = []
                    for k, v in self.typevars.items():
                        if atype == v.type:
                            lst.append(k)
                    returns = {}
                    for x in reversed(lst):
                        for block in self.func_ir.blocks.values():
                            for instr in block.find_insts(ir.Return):
                                value = instr.value
                                if isinstance(value, ir.Var):
                                    name = value.name
                                else:
                                    pass
                                if x == name:
                                    returns[x] = instr
                                    break

                    interped = ""
                    for name, offender in returns.items():
                        loc = getattr(offender, 'loc', ir.unknown_loc)
                        msg = ("Return of: IR name '%s', type '%s', "
                               "location: %s")
                        interped = msg % (name, atype, loc.strformat())
                    return interped

                problem_str = []
                for xtype in rettypes:
                    problem_str.append(_termcolor.errmsg(check_type(xtype)))

                raise TypingError("Can't unify return type from the "
                                  "following types: %s"
                                  % ", ".join(sorted(map(str, rettypes))) +
                                  "\n" + "\n".join(problem_str))
            return unified
        else:
            # Function without a successful return path
            return types.none