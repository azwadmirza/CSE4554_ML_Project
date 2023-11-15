    def analyse_types(self, env):
        if self.doc:
            self.doc = self.doc.analyse_types(env)
            self.doc = self.doc.coerce_to_pyobject(env)
        self.type = py_object_type
        self.is_temp = 1
        return self