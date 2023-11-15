def qname_encode(name: typing.Union[str, typing.Sequence[str]]) -> bytes:
    """Encode QNAME without using name compression.

    Labels (each component of a domain name) are encoded using UTF-8, as that is what
    the Apple TV has been observed to use for all domain names.

    This function can take either a single string, with each label separated by dots, or
    a sequence of strings, and each element of the sequence is treated as a single
    label. A null (empty) label is added for the root domain if it is not already
    present for both types of arguments.
    """
    encoded = bytearray()
    labels: typing.List[str]
    if isinstance(name, collections.abc.Sequence) and not isinstance(name, str):
        # Copy the sequence so we can make changes to it
        labels = list(name) or []
    else:
        # Try to parse it as a service instance name, so we can handle the instance
        # label having dots in it.
        try:
            srv_name = ServiceInstanceName.split_name(name)
        except ValueError:
            labels = typing.cast(str, name).split(".")
        else:
            labels = []
            if srv_name.instance:
                labels.append(srv_name.instance)
            # the ptr_name just has the instance name dropped off
            labels.extend(srv_name.ptr_name.split("."))
    # Ensure there's always an empty label for the root domain
    if not labels or labels[-1] != "":
        labels.append("")
    # DNS-SD uses UTF-8 for names, not IDNA. Apple extends this to basically all places
    # where names are used (except for A/AAAA records, which are transliterated!).
    encoding = "utf-8"
    # Normalize all labels using NFC, as specified in RFC 6763, section 4.1.3
    normalized_labels = (unicodedata.normalize("NFC", label) for label in labels)
    for label in normalized_labels:
        encoded_label = label.encode(encoding)
        encoded_length = len(encoded_label)
        # When truncating the label, we can't just stop at 63 bytes as that might be
        # splitting a multi-byte Unicode codepoint.
        truncated = False
        while encoded_length > 63:
            truncated = True
            truncated_label = encoded_label.decode(encoding)[:-1]
            encoded_label = truncated_label.encode(encoding)
            encoded_length = len(encoded_label)
        if truncated:
            _LOGGER.warning(
                (
                    "A label (%s) is being truncated (to %s) in the DNS name '%s' "
                    "as it is over 63 bytes long."
                ),
                label,
                encoded_label.decode(encoding),
                name,
            )
        encoded.append(encoded_length)
        if encoded_length == 0:
            # If we've reached an empty label, assume this is the last component.
            # Empty labels (two periods right after each other) aren't legal anyways.
            break
        else:
            encoded.extend(encoded_label)
    return encoded