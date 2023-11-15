    def generate_result_code(self, code):
        cname = code.intern_identifier(self.name)
        py_mod_name = self.get_py_mod_name(code)
        qualname = self.get_py_qualified_name(code)
        if self.doc:
            doc_code = self.doc.result()
        else:
            doc_code = '(PyObject *) NULL'
        if self.mkw:
            mkw = self.mkw.py_result()
        else:
            mkw = '(PyObject *) NULL'
        if self.metaclass:
            metaclass = self.metaclass.py_result()
        else:
            metaclass = "(PyObject *) NULL"
        code.putln(
            "%s = __Pyx_Py3MetaclassPrepare(%s, %s, %s, %s, %s, %s, %s); %s" % (
                self.result(),
                metaclass,
                self.bases.result(),
                cname,
                qualname,
                mkw,
                py_mod_name,
                doc_code,
                code.error_goto_if_null(self.result(), self.pos)))
        code.put_gotref(self.py_result())