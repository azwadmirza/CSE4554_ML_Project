    def lower_inst(self, inst):
        # Set debug location for all subsequent LL instructions
        self.debuginfo.mark_location(self.builder, self.loc)
        self.debug_print(str(inst))
        if isinstance(inst, ir.Assign):
            ty = self.typeof(inst.target.name)
            val = self.lower_assign(ty, inst)
            self.storevar(val, inst.target.name)

        elif isinstance(inst, ir.Branch):
            cond = self.loadvar(inst.cond.name)
            tr = self.blkmap[inst.truebr]
            fl = self.blkmap[inst.falsebr]

            condty = self.typeof(inst.cond.name)
            pred = self.context.cast(self.builder, cond, condty, types.boolean)
            assert pred.type == Type.int(1), ("cond is not i1: %s" % pred.type)
            self.builder.cbranch(pred, tr, fl)

        elif isinstance(inst, ir.Jump):
            target = self.blkmap[inst.target]
            self.builder.branch(target)

        elif isinstance(inst, ir.Return):
            if self.generator_info:
                # StopIteration
                self.genlower.return_from_generator(self)
                return
            val = self.loadvar(inst.value.name)
            oty = self.typeof(inst.value.name)
            ty = self.fndesc.restype
            if isinstance(ty, types.Optional):
                # If returning an optional type
                self.call_conv.return_optional_value(self.builder, ty, oty, val)
                return
            if ty != oty:
                val = self.context.cast(self.builder, val, oty, ty)
            retval = self.context.get_return_value(self.builder, ty, val)
            self.call_conv.return_value(self.builder, retval)

        elif isinstance(inst, ir.StaticSetItem):
            signature = self.fndesc.calltypes[inst]
            assert signature is not None
            try:
                impl = self.context.get_function('static_setitem', signature)
            except NotImplementedError:
                return self.lower_setitem(inst.target, inst.index_var,
                                          inst.value, signature)
            else:
                target = self.loadvar(inst.target.name)
                value = self.loadvar(inst.value.name)
                valuety = self.typeof(inst.value.name)
                value = self.context.cast(self.builder, value, valuety,
                                          signature.args[2])
                return impl(self.builder, (target, inst.index, value))

        elif isinstance(inst, ir.Print):
            self.lower_print(inst)

        elif isinstance(inst, ir.SetItem):
            signature = self.fndesc.calltypes[inst]
            assert signature is not None
            return self.lower_setitem(inst.target, inst.index, inst.value,
                                      signature)

        elif isinstance(inst, ir.StoreMap):
            signature = self.fndesc.calltypes[inst]
            assert signature is not None
            return self.lower_setitem(inst.dct, inst.key, inst.value, signature)

        elif isinstance(inst, ir.DelItem):
            target = self.loadvar(inst.target.name)
            index = self.loadvar(inst.index.name)

            targetty = self.typeof(inst.target.name)
            indexty = self.typeof(inst.index.name)

            signature = self.fndesc.calltypes[inst]
            assert signature is not None

            op = operator.delitem
            fnop = self.context.typing_context.resolve_value_type(op)
            callsig = fnop.get_call_type(
                self.context.typing_context, signature.args, {},
            )
            impl = self.context.get_function(fnop, callsig)

            assert targetty == signature.args[0]
            index = self.context.cast(self.builder, index, indexty,
                                      signature.args[1])

            return impl(self.builder, (target, index))

        elif isinstance(inst, ir.Del):
            self.delvar(inst.value)

        elif isinstance(inst, ir.SetAttr):
            target = self.loadvar(inst.target.name)
            value = self.loadvar(inst.value.name)
            signature = self.fndesc.calltypes[inst]

            targetty = self.typeof(inst.target.name)
            valuety = self.typeof(inst.value.name)
            assert signature is not None
            assert signature.args[0] == targetty
            impl = self.context.get_setattr(inst.attr, signature)

            # Convert argument to match
            value = self.context.cast(self.builder, value, valuety,
                                      signature.args[1])

            return impl(self.builder, (target, value))

        elif isinstance(inst, ir.StaticRaise):
            self.lower_static_raise(inst)

        else:
            for _class, func in lower_extensions.items():
                if isinstance(inst, _class):
                    func(self, inst)
                    return
            raise NotImplementedError(type(inst))