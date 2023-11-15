    def generate_result_code(self, code):
        class_def_node = self.class_def_node
        cname = code.intern_identifier(self.name)

        if self.doc:
            code.put_error_if_neg(self.pos,
                'PyDict_SetItem(%s, %s, %s)' % (
                    class_def_node.dict.py_result(),
                    code.intern_identifier(
                        StringEncoding.EncodedString("__doc__")),
                    self.doc.py_result()))
        py_mod_name = self.get_py_mod_name(code)
        qualname = self.get_py_qualified_name(code)
        code.putln(
            '%s = __Pyx_CreateClass(%s, %s, %s, %s, %s); %s' % (
                self.result(),
                class_def_node.bases.py_result(),
                class_def_node.dict.py_result(),
                cname,
                qualname,
                py_mod_name,
                code.error_goto_if_null(self.result(), self.pos)))
        code.put_gotref(self.py_result())