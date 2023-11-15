    def _analyze_assign(self, assign):
        lhs = assign.target.name
        rhs = assign.value
        if isinstance(rhs, ir.Global):
            for T in MAP_TYPES:
                if isinstance(rhs.value, T):
                    self.map_calls.append(lhs)
            if isinstance(rhs.value, pytypes.ModuleType) and rhs.value==numpy:
                self.numpy_globals.append(lhs)
        if isinstance(rhs, ir.Expr) and rhs.op=='getattr':
            if rhs.value.name in self.numpy_globals:
                self.numpy_calls[lhs] = rhs.attr
            elif rhs.value.name in self.numpy_calls:
                # numpy submodule call like np.random.ranf
                # we keep random.ranf as call name
                self.numpy_calls[lhs] = (self.numpy_calls[rhs.value.name]
                    +'.'+rhs.attr)
            elif self._isarray(rhs.value.name):
                self.array_attr_calls[lhs] = (rhs.attr, rhs.value)
        if isinstance(rhs, ir.Expr) and rhs.op=='build_tuple':
            self.tuple_table[lhs] = rhs.items
        if isinstance(rhs, ir.Expr) and rhs.op=='build_list':
            self.list_table[lhs] = rhs.items
        if isinstance(rhs, ir.Const) and isinstance(rhs.value, tuple):
            self.tuple_table[lhs] = rhs.value
        if isinstance(rhs, ir.Const): # and np.isscalar(rhs.value):
            self.constant_table[lhs] = rhs.value

        #rhs_class_out = self._analyze_rhs_classes(rhs)
        size_calls = []
        if self._isarray(lhs):
            analyze_out = self._analyze_rhs_classes(rhs)
            if analyze_out is None:
                rhs_corr = self._add_array_corr(lhs)
            else:
                rhs_corr = copy.copy(analyze_out)
            if lhs in self.array_shape_classes:
                # if shape already inferred in another basic block,
                # make sure this new inference is compatible
                if self.array_shape_classes[lhs]!=rhs_corr:
                    self.array_shape_classes[lhs] = [-1]*self._get_ndims(lhs)
                    self.array_size_vars.pop(lhs, None)
                    if config.DEBUG_ARRAY_OPT==1:
                        print("incompatible array shapes in control flow")
                    return []
            self.array_shape_classes[lhs] = rhs_corr
            self.array_size_vars[lhs] = [-1]*self._get_ndims(lhs)
            # make sure output lhs array has size variables for each dimension
            for (i,corr) in enumerate(rhs_corr):
                # if corr unknown or new
                if corr==-1 or corr not in self.class_sizes.keys():
                    # generate size call nodes for this dimension
                    nodes = self._gen_size_call(assign.target, i)
                    size_calls += nodes
                    assert isinstance(nodes[-1], ir.Assign)
                    size_var = nodes[-1].target
                    if corr!=-1:
                        self.class_sizes[corr] = [size_var]
                    self.array_size_vars[lhs][i] = size_var
                else:
                    # reuse a size variable from this correlation
                    # TODO: consider CFG?
                    self.array_size_vars[lhs][i] = self.class_sizes[corr][0]

        #print(self.array_shape_classes)
        return size_calls