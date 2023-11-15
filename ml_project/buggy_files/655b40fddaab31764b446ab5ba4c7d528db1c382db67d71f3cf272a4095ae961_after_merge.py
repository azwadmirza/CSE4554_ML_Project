    def get_field_nullability(self, field: Union[Field, ForeignObjectRel], method: Optional[str]) -> bool:
        nullable = field.null
        if not nullable and isinstance(field, CharField) and field.blank:
            return True
        if method == '__init__':
            if ((isinstance(field, Field) and field.primary_key)
                    or isinstance(field, ForeignKey)):
                return True
        if method == 'create':
            if isinstance(field, AutoField):
                return True
        if isinstance(field, Field) and field.has_default():
            return True
        return nullable