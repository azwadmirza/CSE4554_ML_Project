    def op_BUILD_CONST_KEY_MAP(self, inst, keys, keytmps, values, res):
        # Unpack the constant key-tuple and reused build_map which takes
        # a sequence of (key, value) pair.
        keyvar = self.get(keys)
        # TODO: refactor this pattern. occurred several times.
        for inst in self.current_block.body:
            if isinstance(inst, ir.Assign) and inst.target is keyvar:
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
                keytup = named_items
                break
        assert len(keytup) == len(values)
        keyconsts = [ir.Const(value=x, loc=self.loc) for x in keytup]
        for kval, tmp in zip(keyconsts, keytmps):
            self.store(kval, tmp)
        items = list(zip(map(self.get, keytmps), map(self.get, values)))
        expr = ir.Expr.build_map(items=items, size=2, loc=self.loc)
        self.store(expr, res)