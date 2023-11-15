    def py_operation_function(self, code):
        type1, type2 = self.operand1.type, self.operand2.type

        if type1 is unicode_type or type2 is unicode_type:
            if type1 in (unicode_type, str_type) and type2 in (unicode_type, str_type):
                is_unicode_concat = True
            elif isinstance(self.operand1, FormattedValueNode) or isinstance(self.operand2, FormattedValueNode):
                # Assume that even if we don't know the second type, it's going to be a string.
                is_unicode_concat = True
            else:
                # Operation depends on the second type.
                is_unicode_concat = False

            if is_unicode_concat:
                if self.operand1.may_be_none() or self.operand2.may_be_none():
                    return '__Pyx_PyUnicode_ConcatSafe'
                else:
                    return '__Pyx_PyUnicode_Concat'

        return super(AddNode, self).py_operation_function(code)