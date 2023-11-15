    def reduce_CreateConstraint(self, *kids):
        r"""%reduce ABSTRACT CONSTRAINT NodeName OptOnExpr \
                    OptExtendingSimple"""
        self.val = qlast.CreateConstraint(
            name=kids[2].val,
            subject=kids[3].val,
            bases=kids[4].val,
        )