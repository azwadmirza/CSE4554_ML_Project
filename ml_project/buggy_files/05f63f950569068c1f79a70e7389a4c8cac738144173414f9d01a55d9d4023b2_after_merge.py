    def generate_evaluation_code(self, code):
        function = self.function
        if function.is_name or function.is_attribute:
            code.globalstate.use_entry_utility_code(function.entry)

        abs_function_cnames = ('abs', 'labs', '__Pyx_abs_longlong')
        is_signed_int = self.type.is_int and self.type.signed
        if self.overflowcheck and is_signed_int and function.result() in abs_function_cnames:
            code.globalstate.use_utility_code(UtilityCode.load_cached("Common", "Overflow.c"))
            code.putln('if (unlikely(%s == __PYX_MIN(%s))) {\
                PyErr_SetString(PyExc_OverflowError,\
                                "Trying to take the absolute value of the most negative integer is not defined."); %s; }' % (
                            self.args[0].result(),
                            self.args[0].type.empty_declaration_code(),
                            code.error_goto(self.pos)))

        if not function.type.is_pyobject or len(self.arg_tuple.args) > 1 or (
                self.arg_tuple.args and self.arg_tuple.is_literal):
            super(SimpleCallNode, self).generate_evaluation_code(code)
            return

        # Special case 0-args and try to avoid explicit tuple creation for Python calls with 1 arg.
        arg = self.arg_tuple.args[0] if self.arg_tuple.args else None
        subexprs = (self.self, self.coerced_self, function, arg)
        for subexpr in subexprs:
            if subexpr is not None:
                subexpr.generate_evaluation_code(code)

        code.mark_pos(self.pos)
        assert self.is_temp
        self.allocate_temp_result(code)

        if arg is None:
            code.globalstate.use_utility_code(UtilityCode.load_cached(
                "PyObjectCallNoArg", "ObjectHandling.c"))
            code.putln(
                "%s = __Pyx_PyObject_CallNoArg(%s); %s" % (
                    self.result(),
                    function.py_result(),
                    code.error_goto_if_null(self.result(), self.pos)))
        else:
            code.globalstate.use_utility_code(UtilityCode.load_cached(
                "PyObjectCallOneArg", "ObjectHandling.c"))
            code.putln(
                "%s = __Pyx_PyObject_CallOneArg(%s, %s); %s" % (
                    self.result(),
                    function.py_result(),
                    arg.py_result(),
                    code.error_goto_if_null(self.result(), self.pos)))

        self.generate_gotref(code)

        for subexpr in subexprs:
            if subexpr is not None:
                subexpr.generate_disposal_code(code)
                subexpr.free_temps(code)