    def analyze_cond_branch(self, map: Optional[Dict[Expression, Type]],
                            node: Expression, context: Optional[Type]) -> Type:
        with self.chk.binder.frame_context():
            if map:
                for var, type in map.items():
                    self.chk.binder.push(var, type)
            return self.accept(node, context=context)