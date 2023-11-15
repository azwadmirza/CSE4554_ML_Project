	def copy(self):
		builder = ParseTreeBuilder(_parsetree_roundtrip=True)
		self.visit(builder)
		return builder.get_parsetree()