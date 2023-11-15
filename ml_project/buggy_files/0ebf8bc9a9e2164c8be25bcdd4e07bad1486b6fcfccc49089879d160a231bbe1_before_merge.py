    def analyse_declarations(self, env):
        class_result = self.classobj
        if self.decorators:
            from .ExprNodes import SimpleCallNode
            for decorator in self.decorators[::-1]:
                class_result = SimpleCallNode(
                    decorator.pos,
                    function=decorator.decorator,
                    args=[class_result])
            self.decorators = None
        self.class_result = class_result
        self.class_result.analyse_declarations(env)
        self.target.analyse_target_declaration(env)
        cenv = self.create_scope(env)
        cenv.directives = env.directives
        cenv.class_obj_cname = self.target.entry.cname
        self.body.analyse_declarations(cenv)