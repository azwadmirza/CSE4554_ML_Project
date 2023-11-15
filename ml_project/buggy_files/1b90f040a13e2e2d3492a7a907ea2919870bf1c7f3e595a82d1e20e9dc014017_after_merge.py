    def check_partial(self, node: Union[DeferredNodeType, FineGrainedDeferredNodeType]) -> None:
        if isinstance(node, MypyFile):
            self.check_top_level(node)
        else:
            self.recurse_into_functions = True
            if isinstance(node, LambdaExpr):
                self.expr_checker.accept(node)
            else:
                self.accept(node)