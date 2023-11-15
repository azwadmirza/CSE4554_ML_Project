    def visit_type_var(self, template: TypeVarType) -> List[Constraint]:
        return [Constraint(template.id, self.direction, self.actual)]