        def op_CALL_FUNCTION_KW(self, inst, func, args, names, res):
            func = self.get(func)
            args = [self.get(x) for x in args]
            # Find names const
            names = self.get(names)
            for inst in self.current_block.body:
                if isinstance(inst, ir.Assign) and inst.target is names:
                    self.current_block.remove(inst)
                    # scan up the block looking for the values, remove them
                    # and find their name strings
                    named_items = []
                    for x in inst.value.items:
                        for y in self.current_block.body[::-1]:
                            if x == y.target:
                                self.current_block.remove(y)
                                named_items.append(y.value.value)
                                break
                    keys = named_items
                    break

            nkeys = len(keys)
            posvals = args[:-nkeys]
            kwvals = args[-nkeys:]
            keyvalues = list(zip(keys, kwvals))

            expr = ir.Expr.call(func, posvals, keyvalues, loc=self.loc)
            self.store(expr, res)