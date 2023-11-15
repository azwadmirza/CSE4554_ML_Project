    def _check_llvm_bugs(self):
        """
        Guard against some well-known LLVM bug(s).
        """
        # Check the locale bug at https://github.com/numba/numba/issues/1569
        # Note we can't cache the result as locale settings can change
        # accross a process's lifetime.  Also, for this same reason,
        # the check here is a mere heuristic (there may be a race condition
        # between now and actually compiling IR).
        ir = """
            define double @func()
            {
                ret double 1.23e+01
            }
            """
        mod = ll.parse_assembly(ir)
        ir_out = str(mod)
        if "12.3" in ir_out or "1.23" in ir_out:
            # Everything ok
            return
        if "1.0" in ir_out:
            loc = locale.getlocale()
            raise RuntimeError(
                "LLVM will produce incorrect floating-point code "
                "in the current locale %s.\nPlease read "
                "http://numba.pydata.org/numba-doc/latest/user/faq.html#llvm-locale-bug "
                "for more information."
                % (loc,))
        raise AssertionError("Unexpected IR:\n%s\n" % (ir_out,))