def qname_encode(name: str) -> bytes:
    """Encode QNAME without using name compression."""
    encoded = bytearray()
    labels = name.split(".")
    # Ensure there's an empty label for the root domain
    if labels[-1] != "":
        labels.append("")
    for label in labels:
        encoded_label = label.encode("idna")
        encoded_length = len(encoded_label)
        # Length of the encoded label, in bytes, but a maximum of 63
        # The maximum is 63 as the upper two bits are used as a flag for name
        # compression.
        encoded.append(min(encoded_length, 63))
        if encoded_length == 0:
            # If we've reached an empty label, assume this is the last component.
            # Empty labels (two periods right after each other) isn't legal anyways.
            break
        if encoded_length > 63:
            _LOGGER.warning(
                (
                    "A label (%s) isn being truncated (to %s) in the DNS name '%s' "
                    "as it is over 63 bytes long."
                ),
                label,
                label[:64],
                name,
            )
            encoded.extend(encoded_label[:64])
        else:
            encoded.extend(encoded_label)
    return encoded