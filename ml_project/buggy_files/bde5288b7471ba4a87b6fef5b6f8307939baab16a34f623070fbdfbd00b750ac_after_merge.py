    def generate_result_code(self, code):
        cname = code.intern_identifier(self.name)
        py_mod_name = self.get_py_mod_name(code)
        qualname = self.get_py_qualified_name(code)
        class_def_node = self.class_def_node
        null = "(PyObject *) NULL"
        doc_code = self.doc.result() if self.doc else null
        mkw = class_def_node.mkw.py_result() if class_def_node.mkw else null
        metaclass = class_def_node.metaclass.py_result() if class_def_node.metaclass else null
        code.putln(
            "%s = __Pyx_Py3MetaclassPrepare(%s, %s, %s, %s, %s, %s, %s); %s" % (
                self.result(),
                metaclass,
                class_def_node.bases.result(),
                cname,
                qualname,
                mkw,
                py_mod_name,
                doc_code,
                code.error_goto_if_null(self.result(), self.pos)))
        code.put_gotref(self.py_result())