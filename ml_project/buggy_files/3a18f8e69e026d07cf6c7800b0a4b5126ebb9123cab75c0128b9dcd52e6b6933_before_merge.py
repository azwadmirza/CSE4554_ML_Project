    def visit_enum(self, type_, **kw):
        if not type_.native_enum or not self.dialect.supports_native_enum:
            return super(PGTypeCompiler, self).visit_enum(type_, **kw)
        else:
            return self.visit_ENUM(type_, **kw)