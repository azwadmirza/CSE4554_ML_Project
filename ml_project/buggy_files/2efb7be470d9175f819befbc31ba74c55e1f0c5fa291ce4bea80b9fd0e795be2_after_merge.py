    def visit_type_var(self, template: TypeVarType) -> List[Constraint]:
        if self.actual:
            return [Constraint(template.id, self.direction, self.actual)]
        else:
            return []