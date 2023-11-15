    def generate_result_code(self, code):
        cname = code.intern_identifier(self.name)

        if self.doc:
            code.put_error_if_neg(self.pos,
                'PyDict_SetItem(%s, %s, %s)' % (
                    self.dict.py_result(),
                    code.intern_identifier(
                        StringEncoding.EncodedString("__doc__")),
                    self.doc.py_result()))
        py_mod_name = self.get_py_mod_name(code)
        qualname = self.get_py_qualified_name(code)
        code.putln(
            '%s = __Pyx_CreateClass(%s, %s, %s, %s, %s); %s' % (
                self.result(),
                self.bases.py_result(),
                self.dict.py_result(),
                cname,
                qualname,
                py_mod_name,
                code.error_goto_if_null(self.result(), self.pos)))
        code.put_gotref(self.py_result())