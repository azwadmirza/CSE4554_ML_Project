    def generate_result_code(self, code):
        bases = self.class_def_node.bases
        mkw = self.class_def_node.mkw
        if mkw:
            code.globalstate.use_utility_code(
                UtilityCode.load_cached("Py3MetaclassGet", "ObjectHandling.c"))
            call = "__Pyx_Py3MetaclassGet(%s, %s)" % (
                bases.result(),
                mkw.result())
        else:
            code.globalstate.use_utility_code(
                UtilityCode.load_cached("CalculateMetaclass", "ObjectHandling.c"))
            call = "__Pyx_CalculateMetaclass(NULL, %s)" % (
                bases.result())
        code.putln(
            "%s = %s; %s" % (
                self.result(), call,
                code.error_goto_if_null(self.result(), self.pos)))
        code.put_gotref(self.py_result())