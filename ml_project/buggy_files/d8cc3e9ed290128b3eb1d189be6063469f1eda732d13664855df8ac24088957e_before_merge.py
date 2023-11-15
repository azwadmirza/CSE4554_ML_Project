    def generate_evaluation_code(self, code):
        function = self.function
        if function.is_name or function.is_attribute:
            code.globalstate.use_entry_utility_code(function.entry)

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

        code.put_gotref(self.py_result())

        for subexpr in subexprs:
            if subexpr is not None:
                subexpr.generate_disposal_code(code)
                subexpr.free_temps(code)