    def generate_result_code(self, code):
        func_type = self.function_type()
        if func_type.is_pyobject:
            arg_code = self.arg_tuple.py_result()
            code.globalstate.use_utility_code(UtilityCode.load_cached(
                "PyObjectCall", "ObjectHandling.c"))
            code.putln(
                "%s = __Pyx_PyObject_Call(%s, %s, NULL); %s" % (
                    self.result(),
                    self.function.py_result(),
                    arg_code,
                    code.error_goto_if_null(self.result(), self.pos)))
            self.generate_gotref(code)
        elif func_type.is_cfunction:
            if self.has_optional_args:
                actual_nargs = len(self.args)
                expected_nargs = len(func_type.args) - func_type.optional_arg_count
                self.opt_arg_struct = code.funcstate.allocate_temp(
                    func_type.op_arg_struct.base_type, manage_ref=True)
                code.putln("%s.%s = %s;" % (
                        self.opt_arg_struct,
                        Naming.pyrex_prefix + "n",
                        len(self.args) - expected_nargs))
                args = list(zip(func_type.args, self.args))
                for formal_arg, actual_arg in args[expected_nargs:actual_nargs]:
                    code.putln("%s.%s = %s;" % (
                            self.opt_arg_struct,
                            func_type.opt_arg_cname(formal_arg.name),
                            actual_arg.result_as(formal_arg.type)))
            exc_checks = []
            if self.type.is_pyobject and self.is_temp:
                exc_checks.append("!%s" % self.result())
            elif self.type.is_memoryviewslice:
                assert self.is_temp
                exc_checks.append(self.type.error_condition(self.result()))
            elif func_type.exception_check != '+':
                exc_val = func_type.exception_value
                exc_check = func_type.exception_check
                if exc_val is not None:
                    exc_checks.append("%s == %s" % (self.result(), func_type.return_type.cast_code(exc_val)))
                if exc_check:
                    if self.nogil:
                        exc_checks.append("__Pyx_ErrOccurredWithGIL()")
                    else:
                        exc_checks.append("PyErr_Occurred()")
            if self.is_temp or exc_checks:
                rhs = self.c_call_code()
                if self.result():
                    lhs = "%s = " % self.result()
                    if self.is_temp and self.type.is_pyobject:
                        #return_type = self.type # func_type.return_type
                        #print "SimpleCallNode.generate_result_code: casting", rhs, \
                        #    "from", return_type, "to pyobject" ###
                        rhs = typecast(py_object_type, self.type, rhs)
                else:
                    lhs = ""
                if func_type.exception_check == '+':
                    translate_cpp_exception(code, self.pos, '%s%s;' % (lhs, rhs),
                                            self.result() if self.type.is_pyobject else None,
                                            func_type.exception_value, self.nogil)
                else:
                    if exc_checks:
                        goto_error = code.error_goto_if(" && ".join(exc_checks), self.pos)
                    else:
                        goto_error = ""
                    code.putln("%s%s; %s" % (lhs, rhs, goto_error))
                if self.type.is_pyobject and self.result():
                    self.generate_gotref(code)
            if self.has_optional_args:
                code.funcstate.release_temp(self.opt_arg_struct)