    def analyse_expressions(self, env):
        if self.bases:
            self.bases = self.bases.analyse_expressions(env)
        if self.metaclass:
            self.metaclass = self.metaclass.analyse_expressions(env)
        if self.mkw:
            self.mkw = self.mkw.analyse_expressions(env)
        self.dict = self.dict.analyse_expressions(env)
        self.class_result = self.class_result.analyse_expressions(env)
        cenv = self.scope
        self.body = self.body.analyse_expressions(cenv)
        self.target.analyse_target_expression(env, self.classobj)
        self.class_cell = self.class_cell.analyse_expressions(cenv)
        return self