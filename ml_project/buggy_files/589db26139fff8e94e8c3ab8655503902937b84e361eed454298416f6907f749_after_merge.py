    def _analyze_np_call(self, call_name, args, kws):
        #print("numpy call ",call_name,args)
        if call_name == 'transpose':
            out_eqs = copy.copy(self.array_shape_classes[args[0].name])
            out_eqs.reverse()
            return out_eqs
        elif call_name in array_creation:
            # these calls (e.g. empty) have only a "shape" argument
            shape_arg = None
            if len(args) > 0:
                shape_arg = args[0]
            elif 'shape' in kws:
                shape_arg = kws['shape']
            else:
                return None
            return self._get_classes_from_shape(shape_arg)
        elif call_name in random_1arg_size:
            # these calls have only a "size" argument
            size_arg = None
            if len(args) > 0:
                size_arg = args[0]
            elif 'size' in kws:
                size_arg = kws['size']
            else:
                return None
            return self._get_classes_from_shape(size_arg)
        elif call_name in random_int_args:
            # e.g. random.rand
            # arguments are integers (not a tuple as in previous calls)
            return self._get_classes_from_dim_args(args)
        elif call_name in random_3arg_sizelast:
            # normal, uniform, ... have 3 args, last one is size
            size_arg = None
            if len(args) == 3:
                size_arg = args[2]
            elif 'size' in kws:
                size_arg = kws['size']
            else:
                return None
            return self._get_classes_from_shape(size_arg)
        elif call_name in random_2arg_sizelast:
            # have 2 args, last one is size
            size_arg = None
            if len(args) == 2:
                size_arg = args[1]
            elif 'size' in kws:
                size_arg = kws['size']
            else:
                return None
            return self._get_classes_from_shape(size_arg)
        elif call_name == 'random.randint':
            # has 4 args, 3rd one is size
            size_arg = None
            if len(args) >= 3:
                size_arg = args[2]
            elif 'size' in kws:
                size_arg = kws['size']
            else:
                return None
            return self._get_classes_from_shape(size_arg)
        elif call_name == 'random.triangular':
            # has 4 args, last one is size
            size_arg = None
            if len(args) == 4:
                size_arg = args[3]
            elif 'size' in kws:
                size_arg = kws['size']
            else:
                return None
            return self._get_classes_from_shape(size_arg)
        elif call_name == 'eye':
            # if one input n, output is n*n
            # two inputs n,m, output is n*m
            # N is either positional or kw arg
            if 'N' in kws:
                assert len(args) == 0
                args.append(kws['N'])
            if 'M' in kws:
                assert len(args) == 1
                args.append(kws['M'])

            new_class1 = self._get_next_class_with_size(args[0].name)
            out_eqs = [new_class1]
            if len(args) > 1:
                new_class2 = self._get_next_class_with_size(args[1].name)
                out_eqs.append(new_class2)
            else:
                out_eqs.append(new_class1)
            return out_eqs
        elif call_name == 'identity':
            # input n, output is n*n
            new_class1 = self._get_next_class_with_size(args[0].name)
            return [new_class1, new_class1]
        elif call_name == 'diag':
            k = self._get_second_arg_or_kw(args, kws, 'k')
            # TODO: support k other than 0 (other diagonal smaller size than
            # main)
            if k == 0:
                in_arr = args[0].name
                in_class = self.array_shape_classes[in_arr][0]
                # if 1D input v, create 2D output with v on diagonal
                # if 2D input v, return v's diagonal
                if self._get_ndims(in_arr) == 1:
                    return [in_class, in_class]
                else:
                    self._get_ndims(in_arr) == 2
                    return [in_class]
        elif call_name in ['empty_like', 'zeros_like', 'ones_like', 'full_like',
                           'copy', 'asfortranarray']:
            # shape same as input
            if args[0].name in self.array_shape_classes:
                out_corrs = copy.copy(self.array_shape_classes[args[0].name])
            else:
                # array scalars: constant input results in 0-dim array
                assert not self._isarray(args[0].name)
                # TODO: make sure arg is scalar
                out_corrs = []
            # asfortranarray converts 0-d to 1-d automatically
            if out_corrs == [] and call_name == 'asfortranarray':
                out_corrs = [CONST_CLASS]
            return out_corrs
        elif call_name == 'reshape':
            #print("reshape args: ", args)
            # TODO: infer shape from length of args[0] in case of -1 input
            if len(args) == 2:
                # shape is either Int or tuple of Int
                return self._get_classes_from_shape(args[1])
            else:
                # a list integers for shape
                return self._get_classes_from_shape_list(args[1:])
        elif call_name == 'array':
            # only 1D list is supported, and not ndmin arg
            if args[0].name in self.list_table:
                l = self.list_table[args[0].name]
                new_class1 = self._get_next_class_with_size(len(l))
                return [new_class1]
        elif call_name == 'concatenate':
            # all dimensions of output are same as inputs, except axis
            axis = self._get_second_arg_or_kw(args, kws, 'axis')
            if axis == -1:  # don't know shape if axis is not constant
                return None
            arr_args = self._get_sequence_arrs(args[0].name)
            if len(arr_args) == 0:
                return None
            ndims = self._get_ndims(arr_args[0].name)
            if ndims <= axis:
                return None
            out_eqs = [-1] * ndims
            new_class1 = self._get_next_class()
            # TODO: set size to sum of input array's size along axis
            out_eqs[axis] = new_class1
            for i in range(ndims):
                if i == axis:
                    continue
                c = self.array_shape_classes[arr_args[0].name][i]
                for v in arr_args:
                    # all input arrays have equal dimensions, except on axis
                    c = self._merge_classes(
                        c, self.array_shape_classes[v.name][i])
                out_eqs[i] = c
            return out_eqs
        elif call_name == 'stack':
            # all dimensions of output are same as inputs, but extra on axis
            axis = self._get_second_arg_or_kw(args, kws, 'axis')
            if axis == -1:  # don't know shape if axis is not constant
                return None
            arr_args = self._get_sequence_arrs(args[0].name)
            if len(arr_args) == 0:
                return None
            ndims = self._get_ndims(arr_args[0].name)
            out_eqs = [-1] * ndims
            # all input arrays have equal dimensions
            for i in range(ndims):
                c = self.array_shape_classes[arr_args[0].name][i]
                for v in arr_args:
                    c = self._merge_classes(
                        c, self.array_shape_classes[v.name][i])
                out_eqs[i] = c
            # output has one extra dimension
            new_class1 = self._get_next_class_with_size(len(arr_args))
            out_eqs.insert(axis, new_class1)
            # TODO: set size to sum of input array's size along axis
            return out_eqs
        elif call_name == 'hstack':
            # hstack is same as concatenate with axis=1 for ndim>=2
            dummy_one_var = ir.Var(args[0].scope, "__dummy_1", args[0].loc)
            self.constant_table["__dummy_1"] = 1
            args.append(dummy_one_var)
            return self._analyze_np_call('concatenate', args, kws)
        elif call_name == 'dstack':
            # dstack is same as concatenate with axis=2, atleast_3d args
            args[0] = self.convert_seq_to_atleast_3d(args[0])
            dummy_two_var = ir.Var(args[0].scope, "__dummy_2", args[0].loc)
            self.constant_table["__dummy_2"] = 2
            args.append(dummy_two_var)
            return self._analyze_np_call('concatenate', args, kws)
        elif call_name == 'vstack':
            # vstack is same as concatenate with axis=0 if 2D input dims or more
            # TODO: set size to sum of input array's size for 1D
            arr_args = self._get_sequence_arrs(args[0].name)
            if len(arr_args) == 0:
                return None
            ndims = self._get_ndims(arr_args[0].name)
            if ndims >= 2:
                dummy_zero_var = ir.Var(
                    args[0].scope, "__dummy_0", args[0].loc)
                self.constant_table["__dummy_0"] = 0
                args.append(dummy_zero_var)
                return self._analyze_np_call('concatenate', args, kws)
        elif call_name == 'column_stack':
            # 1D arrays turn into columns of 2D array
            arr_args = self._get_sequence_arrs(args[0].name)
            if len(arr_args) == 0:
                return None
            c = self.array_shape_classes[arr_args[0].name][0]
            for v in arr_args:
                c = self._merge_classes(c, self.array_shape_classes[v.name][0])
            new_class = self._get_next_class_with_size(len(arr_args))
            return [c, new_class]
        elif call_name in ['cumsum', 'cumprod']:
            in_arr = args[0].name
            in_ndims = self._get_ndims(in_arr)
            # for 1D, output has same size
            # TODO: return flattened size for multi-dimensional input
            if in_ndims == 1:
                return copy.copy(self.array_shape_classes[in_arr])
        elif call_name == 'linspace':
            # default is 50, arg3 is size
            LINSPACE_DEFAULT_SIZE = 50
            size = LINSPACE_DEFAULT_SIZE
            if len(args) >= 3:
                size = args[2].name
            new_class = self._get_next_class_with_size(size)
            return [new_class]
        elif call_name == 'dot':
            # https://docs.scipy.org/doc/numpy/reference/generated/numpy.dot.html
            # for multi-dimensional arrays, last dimension of arg1 and second
            # to last dimension of arg2 should be equal since used in dot product.
            # if arg2 is 1D, its only dimension is used for dot product and
            # should be equal to second to last of arg1.
            assert len(args) == 2 or len(args) == 3
            in1 = args[0].name
            in2 = args[1].name
            ndims1 = self._get_ndims(in1)
            ndims2 = self._get_ndims(in2)
            c1 = self.array_shape_classes[in1][ndims1 - 1]
            c2 = UNKNOWN_CLASS

            if ndims2 == 1:
                c2 = self.array_shape_classes[in2][0]
            else:
                c2 = self.array_shape_classes[in2][ndims2 - 2]

            c_inner = self._merge_classes(c1, c2)

            c_out = []
            for i in range(ndims1 - 1):
                c_out.append(self.array_shape_classes[in1][i])
            for i in range(ndims2 - 2):
                c_out.append(self.array_shape_classes[in2][i])
            if ndims2 > 1:
                c_out.append(self.array_shape_classes[in2][ndims2 - 1])
            return c_out
        elif call_name in UFUNC_MAP_OP:
            return self._broadcast_and_match_shapes([a.name for a in args])

        if config.DEBUG_ARRAY_OPT == 1:
            print("unknown numpy call:", call_name, " ", args)
        return None