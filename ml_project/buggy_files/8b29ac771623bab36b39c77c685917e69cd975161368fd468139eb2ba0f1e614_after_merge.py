def print_federation_field_directive(field: Optional[FieldDefinition]) -> str:
    if not field:
        return ""

    out = ""

    if field.federation.provides:
        out += f' @provides(fields: "{field.federation.provides}")'

    if field.federation.requires:
        out += f' @requires(fields: "{field.federation.requires}")'

    if field.federation.external:
        out += " @external"

    return out