    def reduce_CreateConstraint_CreateFunctionArgs(self, *kids):
        r"""%reduce ABSTRACT CONSTRAINT NodeName CreateFunctionArgs \
                    OptOnExpr OptExtendingSimple"""
        self.val = qlast.CreateConstraint(
            name=kids[2].val,
            params=kids[3].val,
            subject=kids[4].val,
            bases=kids[5].val,
        )