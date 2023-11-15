def make_set_closure_cell():
    """Return a function of two arguments (cell, value) which sets
    the value stored in the closure cell `cell` to `value`.
    """
    # pypy makes this easy. (It also supports the logic below, but
    # why not do the easy/fast thing?)
    if PYPY:

        def set_closure_cell(cell, value):
            cell.__setstate__((value,))

        return set_closure_cell

    # Otherwise gotta do it the hard way.

    # Create a function that will set its first cellvar to `value`.
    def set_first_cellvar_to(value):
        x = value
        return

        # This function will be eliminated as dead code, but
        # not before its reference to `x` forces `x` to be
        # represented as a closure cell rather than a local.
        def force_x_to_be_a_cell():  # pragma: no cover
            return x

    try:
        # Extract the code object and make sure our assumptions about
        # the closure behavior are correct.
        if PY2:
            co = set_first_cellvar_to.func_code
        else:
            co = set_first_cellvar_to.__code__
        if co.co_cellvars != ("x",) or co.co_freevars != ():
            raise AssertionError  # pragma: no cover

        # Convert this code object to a code object that sets the
        # function's first _freevar_ (not cellvar) to the argument.
        if sys.version_info >= (3, 8):
            # CPython 3.8+ has an incompatible CodeType signature
            # (added a posonlyargcount argument) but also added
            # CodeType.replace() to do this without counting parameters.
            set_first_freevar_code = co.replace(
                co_cellvars=co.co_freevars, co_freevars=co.co_cellvars
            )
        else:
            args = [co.co_argcount]
            if not PY2:
                args.append(co.co_kwonlyargcount)
            args.extend(
                [
                    co.co_nlocals,
                    co.co_stacksize,
                    co.co_flags,
                    co.co_code,
                    co.co_consts,
                    co.co_names,
                    co.co_varnames,
                    co.co_filename,
                    co.co_name,
                    co.co_firstlineno,
                    co.co_lnotab,
                    # These two arguments are reversed:
                    co.co_cellvars,
                    co.co_freevars,
                ]
            )
            set_first_freevar_code = types.CodeType(*args)

        def set_closure_cell(cell, value):
            # Create a function using the set_first_freevar_code,
            # whose first closure cell is `cell`. Calling it will
            # change the value of that cell.
            setter = types.FunctionType(
                set_first_freevar_code, {}, "setter", (), (cell,)
            )
            # And call it to set the cell.
            setter(value)

        # Make sure it works on this interpreter:
        def make_func_with_cell():
            x = None

            def func():
                return x  # pragma: no cover

            return func

        if PY2:
            cell = make_func_with_cell().func_closure[0]
        else:
            cell = make_func_with_cell().__closure__[0]
        set_closure_cell(cell, 100)
        if cell.cell_contents != 100:
            raise AssertionError  # pragma: no cover

    except Exception:
        return just_warn
    else:
        return set_closure_cell