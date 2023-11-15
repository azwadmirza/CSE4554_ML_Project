    def py_operation_function(self, code):
        is_unicode_concat = False
        if isinstance(self.operand1, FormattedValueNode) or isinstance(self.operand2, FormattedValueNode):
            is_unicode_concat = True
        else:
            type1, type2 = self.operand1.type, self.operand2.type
            if type1 is unicode_type or type2 is unicode_type:
                is_unicode_concat = type1.is_builtin_type and type2.is_builtin_type

        if is_unicode_concat:
            if self.operand1.may_be_none() or self.operand2.may_be_none():
                return '__Pyx_PyUnicode_ConcatSafe'
            else:
                return '__Pyx_PyUnicode_Concat'
        return super(AddNode, self).py_operation_function(code)