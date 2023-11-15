    def analyse_types(self, env):
        self.bases = self.bases.analyse_types(env)
        if self.doc:
            self.doc = self.doc.analyse_types(env)
            self.doc = self.doc.coerce_to_pyobject(env)
        env.use_utility_code(UtilityCode.load_cached("CreateClass", "ObjectHandling.c"))
        return self