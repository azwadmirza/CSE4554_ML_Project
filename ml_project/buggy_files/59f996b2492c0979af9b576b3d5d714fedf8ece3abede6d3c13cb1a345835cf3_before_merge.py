    def generate_result_code(self, code):
        code.globalstate.use_utility_code(UtilityCode.load_cached("Py3ClassCreate", "ObjectHandling.c"))
        cname = code.intern_identifier(self.name)
        if self.mkw:
            mkw = self.mkw.py_result()
        else:
            mkw = 'NULL'
        if self.metaclass:
            metaclass = self.metaclass.py_result()
        else:
            metaclass = "((PyObject*)&__Pyx_DefaultClassType)"
        code.putln(
            '%s = __Pyx_Py3ClassCreate(%s, %s, %s, %s, %s, %d, %d); %s' % (
                self.result(),
                metaclass,
                cname,
                self.bases.py_result(),
                self.dict.py_result(),
                mkw,
                self.calculate_metaclass,
                self.allow_py2_metaclass,
                code.error_goto_if_null(self.result(), self.pos)))
        code.put_gotref(self.py_result())