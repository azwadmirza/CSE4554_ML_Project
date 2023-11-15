    def generate_evaluation_code(self, code):
        code.mark_pos(self.pos)
        self.allocate_temp_result(code)

        self.function.generate_evaluation_code(code)
        assert self.arg_tuple.mult_factor is None
        args = self.arg_tuple.args
        for arg in args:
            arg.generate_evaluation_code(code)

        # make sure function is in temp so that we can replace the reference below if it's a method
        reuse_function_temp = self.function.is_temp
        if reuse_function_temp:
            function = self.function.result()
        else:
            function = code.funcstate.allocate_temp(py_object_type, manage_ref=True)
            self.function.make_owned_reference(code)
            code.put("%s = %s; " % (function, self.function.py_result()))
            self.function.generate_disposal_code(code)
            self.function.free_temps(code)

        self_arg = code.funcstate.allocate_temp(py_object_type, manage_ref=True)
        code.putln("%s = NULL;" % self_arg)
        arg_offset_cname = None
        if len(args) > 1:
            arg_offset_cname = code.funcstate.allocate_temp(PyrexTypes.c_int_type, manage_ref=False)
            code.putln("%s = 0;" % arg_offset_cname)

        def attribute_is_likely_method(attr):
            obj = attr.obj
            if obj.is_name and obj.entry.is_pyglobal:
                return False  # more likely to be a function
            return True

        if self.function.is_attribute:
            likely_method = 'likely' if attribute_is_likely_method(self.function) else 'unlikely'
        elif self.function.is_name and self.function.cf_state:
            # not an attribute itself, but might have been assigned from one (e.g. bound method)
            for assignment in self.function.cf_state:
                value = assignment.rhs
                if value and value.is_attribute and value.obj.type.is_pyobject:
                    if attribute_is_likely_method(value):
                        likely_method = 'likely'
                        break
            else:
                likely_method = 'unlikely'
        else:
            likely_method = 'unlikely'

        code.putln("if (CYTHON_UNPACK_METHODS && %s(PyMethod_Check(%s))) {" % (likely_method, function))
        code.putln("%s = PyMethod_GET_SELF(%s);" % (self_arg, function))
        # the following is always true in Py3 (kept only for safety),
        # but is false for unbound methods in Py2
        code.putln("if (likely(%s)) {" % self_arg)
        code.putln("PyObject* function = PyMethod_GET_FUNCTION(%s);" % function)
        code.put_incref(self_arg, py_object_type)
        code.put_incref("function", py_object_type)
        # free method object as early to possible to enable reuse from CPython's freelist
        code.put_decref_set(function, "function")
        if len(args) > 1:
            code.putln("%s = 1;" % arg_offset_cname)
        code.putln("}")
        code.putln("}")

        if not args:
            # fastest special case: try to avoid tuple creation
            code.globalstate.use_utility_code(
                UtilityCode.load_cached("PyObjectCallNoArg", "ObjectHandling.c"))
            code.globalstate.use_utility_code(
                UtilityCode.load_cached("PyObjectCallOneArg", "ObjectHandling.c"))
            code.putln(
                "%s = (%s) ? __Pyx_PyObject_CallOneArg(%s, %s) : __Pyx_PyObject_CallNoArg(%s);" % (
                    self.result(), self_arg,
                    function, self_arg,
                    function))
            code.put_xdecref_clear(self_arg, py_object_type)
            code.funcstate.release_temp(self_arg)
            code.putln(code.error_goto_if_null(self.result(), self.pos))
            code.put_gotref(self.py_result())
        elif len(args) == 1:
            # fastest special case: try to avoid tuple creation
            code.globalstate.use_utility_code(
                UtilityCode.load_cached("PyObjectCall2Args", "ObjectHandling.c"))
            code.globalstate.use_utility_code(
                UtilityCode.load_cached("PyObjectCallOneArg", "ObjectHandling.c"))
            arg = args[0]
            code.putln(
                "%s = (%s) ? __Pyx_PyObject_Call2Args(%s, %s, %s) : __Pyx_PyObject_CallOneArg(%s, %s);" % (
                    self.result(), self_arg,
                    function, self_arg, arg.py_result(),
                    function, arg.py_result()))
            code.put_xdecref_clear(self_arg, py_object_type)
            code.funcstate.release_temp(self_arg)
            arg.generate_disposal_code(code)
            arg.free_temps(code)
            code.putln(code.error_goto_if_null(self.result(), self.pos))
            code.put_gotref(self.py_result())
        else:
            code.globalstate.use_utility_code(
                UtilityCode.load_cached("PyFunctionFastCall", "ObjectHandling.c"))
            code.globalstate.use_utility_code(
                UtilityCode.load_cached("PyCFunctionFastCall", "ObjectHandling.c"))
            for test_func, call_prefix in [('PyFunction_Check', 'Py'), ('__Pyx_PyFastCFunction_Check', 'PyC')]:
                code.putln("#if CYTHON_FAST_%sCALL" % call_prefix.upper())
                code.putln("if (%s(%s)) {" % (test_func, function))
                code.putln("PyObject *%s[%d] = {%s, %s};" % (
                    Naming.quick_temp_cname,
                    len(args)+1,
                    self_arg,
                    ', '.join(arg.py_result() for arg in args)))
                code.putln("%s = __Pyx_%sFunction_FastCall(%s, %s+1-%s, %d+%s); %s" % (
                    self.result(),
                    call_prefix,
                    function,
                    Naming.quick_temp_cname,
                    arg_offset_cname,
                    len(args),
                    arg_offset_cname,
                    code.error_goto_if_null(self.result(), self.pos)))
                code.put_xdecref_clear(self_arg, py_object_type)
                code.put_gotref(self.py_result())
                for arg in args:
                    arg.generate_disposal_code(code)
                code.putln("} else")
                code.putln("#endif")

            code.putln("{")
            args_tuple = code.funcstate.allocate_temp(py_object_type, manage_ref=True)
            code.putln("%s = PyTuple_New(%d+%s); %s" % (
                args_tuple, len(args), arg_offset_cname,
                code.error_goto_if_null(args_tuple, self.pos)))
            code.put_gotref(args_tuple)

            if len(args) > 1:
                code.putln("if (%s) {" % self_arg)
            code.putln("__Pyx_GIVEREF(%s); PyTuple_SET_ITEM(%s, 0, %s); %s = NULL;" % (
                self_arg, args_tuple, self_arg, self_arg))  # stealing owned ref in this case
            code.funcstate.release_temp(self_arg)
            if len(args) > 1:
                code.putln("}")

            for i, arg in enumerate(args):
                arg.make_owned_reference(code)
                code.put_giveref(arg.py_result())
                code.putln("PyTuple_SET_ITEM(%s, %d+%s, %s);" % (
                    args_tuple, i, arg_offset_cname, arg.py_result()))
            if len(args) > 1:
                code.funcstate.release_temp(arg_offset_cname)

            for arg in args:
                arg.generate_post_assignment_code(code)
                arg.free_temps(code)

            code.globalstate.use_utility_code(
                UtilityCode.load_cached("PyObjectCall", "ObjectHandling.c"))
            code.putln(
                "%s = __Pyx_PyObject_Call(%s, %s, NULL); %s" % (
                    self.result(),
                    function, args_tuple,
                    code.error_goto_if_null(self.result(), self.pos)))
            code.put_gotref(self.py_result())

            code.put_decref_clear(args_tuple, py_object_type)
            code.funcstate.release_temp(args_tuple)

            if len(args) == 1:
                code.putln("}")
            code.putln("}")  # !CYTHON_FAST_PYCALL

        if reuse_function_temp:
            self.function.generate_disposal_code(code)
            self.function.free_temps(code)
        else:
            code.put_decref_clear(function, py_object_type)
            code.funcstate.release_temp(function)