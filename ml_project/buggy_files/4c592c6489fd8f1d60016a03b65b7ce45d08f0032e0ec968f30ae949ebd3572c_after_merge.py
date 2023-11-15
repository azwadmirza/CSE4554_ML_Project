    def get_arglist(I_type, T_type):
        """
        Generate argument list for calling the C++ function
        """
        args = []
        next_is_writeable = False
        j = 0
        for t in arg_spec:
            const = '' if next_is_writeable else 'const '
            next_is_writeable = False
            if t == '*':
                next_is_writeable = True
                continue
            elif t == 'i':
                args.append("*(%s*)a[%d]" % (const + I_type, j))
            elif t == 'I':
                args.append("(%s*)a[%d]" % (const + I_type, j))
            elif t == 'T':
                args.append("(%s*)a[%d]" % (const + T_type, j))
            elif t == 'B':
                args.append("(npy_bool_wrapper*)a[%d]" % (j,))
            elif t == 'V':
                if const:
                    raise ValueError("'V' argument must be an output arg")
                args.append("(std::vector<%s>*)a[%d]" % (I_type, j,))
            elif t == 'W':
                if const:
                    raise ValueError("'W' argument must be an output arg")
                args.append("(std::vector<%s>*)a[%d]" % (T_type, j,))
            elif t == 'l':
                args.append("*(%snpy_int64*)a[%d]" % (const, j))
            else:
                raise ValueError("Invalid spec character %r" % (t,))
            j += 1
        return ", ".join(args)