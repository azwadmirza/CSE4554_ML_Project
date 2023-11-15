def clean(fields):
    visitor.visit_fields(fields, fieldset_func=schema_cleanup, field_func=field_cleanup)