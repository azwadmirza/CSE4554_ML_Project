    def as_cclass(self):
        """
        Return this node as if it were declared as an extension class
        """
        if self.is_py3_style_class:
            error(self.classobj.pos, "Python3 style class could not be represented as C class")
            return

        from . import ExprNodes
        return CClassDefNode(self.pos,
                             visibility='private',
                             module_name=None,
                             class_name=self.name,
                             bases=self.bases or ExprNodes.TupleNode(self.pos, args=[]),
                             decorators=self.decorators,
                             body=self.body,
                             in_pxd=False,
                             doc=self.doc)