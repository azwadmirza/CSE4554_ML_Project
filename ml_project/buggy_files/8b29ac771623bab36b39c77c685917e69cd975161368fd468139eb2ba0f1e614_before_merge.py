def print_federation_field_directive(field, metadata):
    out = ""

    if metadata and "federation" in metadata:
        federation = metadata["federation"]

        provides = federation.get("provides", "")
        requires = federation.get("requires", "")
        external = federation.get("external", False)

        if provides:
            out += f' @provides(fields: "{provides}")'

        if requires:
            out += f' @requires(fields: "{requires}")'

        if external:
            out += " @external"

    return out