    def generate_result_code(self, code):
        code.globalstate.use_utility_code(UtilityCode.load_cached("Py3ClassCreate", "ObjectHandling.c"))
        cname = code.intern_identifier(self.name)
        class_def_node = self.class_def_node
        mkw = class_def_node.mkw.py_result() if class_def_node.mkw else 'NULL'
        if class_def_node.metaclass:
            metaclass = class_def_node.metaclass.py_result()
        else:
            metaclass = "((PyObject*)&__Pyx_DefaultClassType)"
        code.putln(
            '%s = __Pyx_Py3ClassCreate(%s, %s, %s, %s, %s, %d, %d); %s' % (
                self.result(),
                metaclass,
                cname,
                class_def_node.bases.py_result(),
                class_def_node.dict.py_result(),
                mkw,
                self.calculate_metaclass,
                self.allow_py2_metaclass,
                code.error_goto_if_null(self.result(), self.pos)))
        code.put_gotref(self.py_result())