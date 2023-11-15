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

                    for name, offender in returns.items():
                        loc = getattr(offender, 'loc', ir.unknown_loc)
                        msg = ("Return of: IR name '%s', type '%s', "
                               "location: %s")
                        interped = msg % (name, atype, loc.strformat())
                    return interped