def clean(fields, strict=False):
    global strict_mode
    strict_mode = strict
    visitor.visit_fields(fields, fieldset_func=schema_cleanup, field_func=field_cleanup)