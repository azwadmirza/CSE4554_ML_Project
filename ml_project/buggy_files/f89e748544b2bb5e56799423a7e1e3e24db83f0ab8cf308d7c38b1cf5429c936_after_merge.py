    def _analyze_inst(self, label, scope, equiv_set, inst, redefined):
        pre = []
        post = []
        if config.DEBUG_ARRAY_OPT >= 2:
            print("analyze_inst:", inst)
        if isinstance(inst, ir.Assign):
            lhs = inst.target
            typ = self.typemap[lhs.name]
            shape = None
            if isinstance(typ, types.ArrayCompatible) and typ.ndim == 0:
                shape = ()
            elif isinstance(inst.value, ir.Expr):
                result = self._analyze_expr(scope, equiv_set, inst.value)
                if result:
                    shape = result[0]
                    pre = result[1]
                    if len(result) > 2:
                        rhs = result[2]
                        inst.value = rhs
            elif (isinstance(inst.value, ir.Var) or
                  isinstance(inst.value, ir.Const)):
                shape = inst.value

            if isinstance(shape, ir.Const):
                if isinstance(shape.value, tuple):
                    loc = shape.loc
                    shape = tuple(ir.Const(x, loc) for x in shape.value)
                elif isinstance(shape.value, int):
                    shape = (shape,)
                else:
                    shape = None
            elif (isinstance(shape, ir.Var) and
                  isinstance(self.typemap[shape.name], types.Integer)):
                shape = (shape,)
            elif isinstance(shape, WrapIndexMeta):
                """ Here we've got the special WrapIndexMeta object
                    back from analyzing a wrap_index call.  We define
                    the lhs and then get it's equivalence class then
                    add the mapping from the tuple of slice size and
                    dimensional size equivalence ids to the lhs
                    equivalence id.
                """
                equiv_set.define(lhs, redefined, self.func_ir, typ)
                lhs_ind = equiv_set._get_ind(lhs.name)
                if lhs_ind != -1:
                    equiv_set.wrap_map[(shape.slice_size, shape.dim_size)] = lhs_ind
                return pre, post

            if isinstance(typ, types.ArrayCompatible):
                if (shape == None or isinstance(shape, tuple) or
                    (isinstance(shape, ir.Var) and
                     not equiv_set.has_shape(shape))):
                    (shape, post) = self._gen_shape_call(equiv_set, lhs,
                                                         typ.ndim, shape)
            elif isinstance(typ, types.UniTuple):
                if shape and isinstance(typ.dtype, types.Integer):
                    (shape, post) = self._gen_shape_call(equiv_set, lhs,
                                                         len(typ), shape)

            if shape != None:
                equiv_set.insert_equiv(lhs, shape)
            equiv_set.define(lhs, redefined, self.func_ir, typ)
        elif isinstance(inst, ir.StaticSetItem) or isinstance(inst, ir.SetItem):
            index = inst.index if isinstance(inst, ir.SetItem) else inst.index_var
            result = guard(self._index_to_shape,
                scope, equiv_set, inst.target, index)
            if not result:
                return [], []
            if result[0] is not None:
                assert(isinstance(inst, ir.SetItem))
                inst.index = result[0]
                #inst.index_var = result[0]
            result = result[1]
            (target_shape, pre) = result
            value_shape = equiv_set.get_shape(inst.value)
            if value_shape == (): # constant
                equiv_set.set_shape_setitem(inst, target_shape)
                return pre, []
            elif value_shape != None:
                target_typ = self.typemap[inst.target.name]
                require(isinstance(target_typ, types.ArrayCompatible))
                target_ndim = target_typ.ndim
                shapes = [target_shape, value_shape]
                names = [inst.target.name, inst.value.name]
                shape, asserts = self._broadcast_assert_shapes(
                                scope, equiv_set, inst.loc, shapes, names)
                n = len(shape)
                # shape dimension must be within target dimension
                assert(target_ndim >= n)
                equiv_set.set_shape_setitem(inst, shape)
                return pre + asserts, []
            else:
                return pre, []
        elif isinstance(inst, ir.Branch):
            cond_var = inst.cond
            cond_def = guard(get_definition, self.func_ir, cond_var)
            if not cond_def:  # phi variable has no single definition
                # We'll use equiv_set to try to find a cond_def instead
                equivs = equiv_set.get_equiv_set(cond_var)
                defs = []
                for name in equivs:
                    if isinstance(name, str) and name in self.typemap:
                        var_def = guard(get_definition, self.func_ir, name,
                                        lhs_only=True)
                        if isinstance(var_def, ir.Var):
                            var_def = var_def.name
                        if var_def:
                            defs.append(var_def)
                    else:
                        defs.append(name)
                defvars = set(filter(lambda x: isinstance(x, str), defs))
                defconsts = set(defs).difference(defvars)
                if len(defconsts) == 1:
                    cond_def = list(defconsts)[0]
                elif len(defvars) == 1:
                    cond_def = guard(get_definition, self.func_ir,
                                     list(defvars)[0])
            if isinstance(cond_def, ir.Expr) and cond_def.op == 'binop':
                br = None
                if cond_def.fn == operator.eq:
                    br = inst.truebr
                    otherbr = inst.falsebr
                    cond_val = 1
                elif cond_def.fn == operator.ne:
                    br = inst.falsebr
                    otherbr = inst.truebr
                    cond_val = 0
                lhs_typ = self.typemap[cond_def.lhs.name]
                rhs_typ = self.typemap[cond_def.rhs.name]
                if (br != None and
                    ((isinstance(lhs_typ, types.Integer) and
                      isinstance(rhs_typ, types.Integer)) or
                     (isinstance(lhs_typ, types.BaseTuple) and
                      isinstance(rhs_typ, types.BaseTuple)))):
                    loc = inst.loc
                    args = (cond_def.lhs, cond_def.rhs)
                    asserts = self._make_assert_equiv(
                        scope, loc, equiv_set, args)
                    asserts.append(
                        ir.Assign(ir.Const(cond_val, loc), cond_var, loc))
                    self.prepends[(label, br)] = asserts
                    self.prepends[(label, otherbr)] = [
                        ir.Assign(ir.Const(1 - cond_val, loc), cond_var, loc)]
            else:
                if isinstance(cond_def, ir.Const):
                    cond_def = cond_def.value
                if isinstance(cond_def, int) or isinstance(cond_def, bool):
                    # condition is always true/false, prune the outgoing edge
                    pruned_br = inst.falsebr if cond_def else inst.truebr
                    if pruned_br in self.pruned_predecessors:
                        self.pruned_predecessors[pruned_br].append(label)
                    else:
                        self.pruned_predecessors[pruned_br] = [label]

        elif type(inst) in array_analysis_extensions:
            # let external calls handle stmt if type matches
            f = array_analysis_extensions[type(inst)]
            pre, post = f(inst, equiv_set, self.typemap, self)

        return pre, post