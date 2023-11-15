def parse_domain_name(buffer: typing.BinaryIO) -> str:
    """Unpack a domain name, handling any name compression encountered.

    Basically, each component of a domain name (called a "label") is prefixed with a
    length followed by the encoded label. The final component has a zero length
    with a null label for the DNS root. The tricky part is that labels are limited to 63
    bytes, and the upper two bits of the length are used as a flag for "name
    compression". For full details, see RFC 1035, sections 3.1 and 4.1.4.

    If labels start with the "ASCII Compatible Encoding" prefix ("xn--"), they are
    decoded with IDNA. Otherwise each label is decoded as UTF-8, as that is what is used
    for DNS-SD and Apple doesn't seem to use IDNA anywhere in their mDNS/DNS-SD stack.

    This is distinct from "character-string" encoding; use `parse_string` for that.
    """
    labels = []
    compression_offset = None
    while buffer:
        length = unpack_stream(">B", buffer)[0]
        if length == 0:
            break
        # The two high bits of the length are a flag for DNS name compression
        length_flags = (length & 0xC0) >> 6
        # The 10 and 01 flags are reserved
        assert length_flags in (0, 0b11)
        if length_flags == 0b11:
            # Mask off the upper two bits, then concatenate the next byte from the
            # stream to get the offset.
            high_bits: int = length & 0x3F
            new_offset_data = bytearray(buffer.read(1))
            new_offset_data.insert(0, high_bits)
            new_offset = struct.unpack(">H", new_offset_data)[0]
            # I think it's technically possible to have multiple levels of name
            # compression, so make sure we don't lose the original place we need to go
            # back to.
            if compression_offset is None:
                compression_offset = buffer.tell()
            buffer.seek(new_offset)
        elif length_flags == 0:
            label = buffer.read(length)
            if label[:4] == b"xn--":
                decoded_label = label.decode("idna")
            else:
                decoded_label = label.decode("utf-8")
            labels.append(decoded_label)
    if compression_offset is not None:
        buffer.seek(compression_offset)
    return ".".join(labels)