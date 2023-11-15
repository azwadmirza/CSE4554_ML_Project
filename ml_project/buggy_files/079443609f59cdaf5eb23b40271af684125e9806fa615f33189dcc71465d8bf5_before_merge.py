    def generate_assignment_code(self, rhs, code, overloaded_assignment=False,
        exception_check=None, exception_value=None):
        self.generate_subexpr_evaluation_code(code)

        if self.type.is_pyobject:
            self.generate_setitem_code(rhs.py_result(), code)
        elif self.base.type is bytearray_type:
            value_code = self._check_byte_value(code, rhs)
            self.generate_setitem_code(value_code, code)
        elif self.base.type.is_cpp_class and self.exception_check and self.exception_check == '+':
            if overloaded_assignment and exception_check and \
                self.exception_value != exception_value:
                # Handle the case that both the index operator and the assignment
                # operator have a c++ exception handler and they are not the same.
                translate_double_cpp_exception(code, self.pos, self.type,
                    self.result(), rhs.result(), self.exception_value,
                    exception_value, self.in_nogil_context)
            else:
                # Handle the case that only the index operator has a
                # c++ exception handler, or that
                # both exception handlers are the same.
                translate_cpp_exception(code, self.pos,
                    "%s = %s;" % (self.result(), rhs.result()),
                    self.result() if self.lhs.is_pyobject else None,
                    self.exception_value, self.in_nogil_context)
        else:
            code.putln(
                "%s = %s;" % (self.result(), rhs.result()))

        self.generate_subexpr_disposal_code(code)
        self.free_subexpr_temps(code)
        rhs.generate_disposal_code(code)
        rhs.free_temps(code)