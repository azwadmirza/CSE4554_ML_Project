    def _analyze_rhs_classes(self, node):
        if isinstance(node, ir.Arg):
            assert self._isarray(node.name)
            return self._add_array_corr(node.name)
        elif isinstance(node, ir.Var):
            return copy.copy(self.array_shape_classes[node.name])
        elif isinstance(node, (ir.Global,ir.FreeVar)):
            # XXX: currently, global variables are frozen in Numba (can change)
            if isinstance(node.value, numpy.ndarray):
                shape = node.value.shape
                out_eqs = []
                for c in shape:
                    new_class = self._get_next_class_with_size(c)
                    out_eqs.append(new_class)
                return out_eqs
        elif isinstance(node, ir.Expr):
            if node.op=='unary' and node.fn in UNARY_MAP_OP:
                assert isinstance(node.value, ir.Var)
                in_var = node.value.name
                assert self._isarray(in_var)
                return copy.copy(self.array_shape_classes[in_var])
            elif node.op=='binop' and node.fn in BINARY_MAP_OP:
                arg1 = node.lhs.name
                arg2 = node.rhs.name
                return self._broadcast_and_match_shapes([arg1, arg2])
            elif node.op=='inplace_binop' and node.immutable_fn in BINARY_MAP_OP:
                arg1 = node.lhs.name
                arg2 = node.rhs.name
                return self._broadcast_and_match_shapes([arg1, arg2])
            elif node.op=='arrayexpr':
                # set to remove duplicates
                args = {v.name for v in node.list_vars()}
                return self._broadcast_and_match_shapes(list(args))
            elif node.op=='cast':
                return copy.copy(self.array_shape_classes[node.value.name])
            elif node.op=='call':
                call_name = 'NULL'
                args = copy.copy(node.args)
                if node.func.name in self.map_calls:
                    return copy.copy(self.array_shape_classes[args[0].name])
                if node.func.name in self.numpy_calls.keys():
                    call_name = self.numpy_calls[node.func.name]
                elif node.func.name in self.array_attr_calls.keys():
                    call_name, arr = self.array_attr_calls[node.func.name]
                    args.insert(0, arr)
                if call_name is not 'NULL':
                    return self._analyze_np_call(call_name, args, dict(node.kws))
                else:
                    if config.DEBUG_ARRAY_OPT==1:
                        # no need to raise since this is not a failure and
                        # analysis can continue (might limit optimization later)
                        print("can't find shape for unknown call:", node)
                    return None
            elif node.op=='getattr' and self._isarray(node.value.name):
                # numpy recarray, e.g. X.a
                val = node.value.name
                val_typ = self.typemap[val]
                if (isinstance(val_typ.dtype, types.npytypes.Record)
                        and node.attr in val_typ.dtype.fields):
                    return copy.copy(self.array_shape_classes[val])
                # matrix transpose
                if node.attr=='T':
                    return self._analyze_np_call('transpose', [node.value],
                        dict())
            elif (node.op=='getattr' and isinstance(
                    self.typemap[node.value.name], types.npytypes.Record)):
                # nested arrays in numpy records
                val = node.value.name
                val_typ = self.typemap[val]
                if (node.attr in val_typ.fields
                        and isinstance(val_typ.fields[node.attr][0],
                        types.npytypes.NestedArray)):
                    shape = val_typ.fields[node.attr][0].shape
                    return self._get_classes_from_const_shape(shape)
            elif node.op=='getitem' or node.op=='static_getitem':
                # getitem where output is array is possibly accessing elements
                # of numpy records, e.g. X['a']
                val = node.value.name
                val_typ = self.typemap[val]
                if (self._isarray(val) and isinstance(val_typ.dtype,
                        types.npytypes.Record)
                        and node.index in val_typ.dtype.fields):
                    return copy.copy(self.array_shape_classes[val])
            else:
                if config.DEBUG_ARRAY_OPT==1:
                    # no need to raise since this is not a failure and
                    # analysis can continue (might limit optimization later)
                    print("can't find shape classes for expr",node," of op",node.op)
        if config.DEBUG_ARRAY_OPT==1:
            # no need to raise since this is not a failure and
            # analysis can continue (might limit optimization later)
            print("can't find shape classes for node",node," of type ",type(node))
        return None