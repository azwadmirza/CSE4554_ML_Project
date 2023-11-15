def get_pem_entry(text, pem_type=None):
    """
    Returns a properly formatted PEM string from the input text fixing
    any whitespace or line-break issues

    text:
        Text containing the X509 PEM entry to be returned or path to
        a file containing the text.

    pem_type:
        If specified, this function will only return a pem of a certain type,
        for example 'CERTIFICATE' or 'CERTIFICATE REQUEST'.

    CLI Example:

    .. code-block:: bash

        salt '*' x509.get_pem_entry "-----BEGIN CERTIFICATE REQUEST-----MIICyzCC Ar8CAQI...-----END CERTIFICATE REQUEST"
    """
    text = _text_or_file(text)
    # Replace encoded newlines
    text = text.replace("\\n", "\n")

    if (
        len(text.splitlines()) == 1
        and text.startswith("-----")
        and text.endswith("-----")
    ):
        # mine.get returns the PEM on a single line, we fix this
        pem_fixed = []
        pem_temp = text
        while len(pem_temp) > 0:
            if pem_temp.startswith("-----"):
                # Grab ----(.*)---- blocks
                pem_fixed.append(pem_temp[: pem_temp.index("-----", 5) + 5])
                pem_temp = pem_temp[pem_temp.index("-----", 5) + 5 :]
            else:
                # grab base64 chunks
                if pem_temp[:64].count("-") == 0:
                    pem_fixed.append(pem_temp[:64])
                    pem_temp = pem_temp[64:]
                else:
                    pem_fixed.append(pem_temp[: pem_temp.index("-")])
                    pem_temp = pem_temp[pem_temp.index("-") :]
        text = "\n".join(pem_fixed)

    errmsg = "PEM text not valid:\n{}".format(text)
    if pem_type:
        errmsg = "PEM does not contain a single entry of type {}:\n" "{}".format(
            pem_type, text
        )

    _match = _valid_pem(text, pem_type)
    if not _match:
        raise salt.exceptions.SaltInvocationError(errmsg)

    _match_dict = _match.groupdict()
    pem_header = _match_dict["pem_header"]
    proc_type = _match_dict["proc_type"]
    dek_info = _match_dict["dek_info"]
    pem_footer = _match_dict["pem_footer"]
    pem_body = _match_dict["pem_body"]

    # Remove all whitespace from body
    pem_body = "".join(pem_body.split())

    # Generate correctly formatted pem
    ret = pem_header + "\n"
    if proc_type:
        ret += proc_type + "\n"
    if dek_info:
        ret += dek_info + "\n" + "\n"
    for i in range(0, len(pem_body), 64):
        ret += pem_body[i : i + 64] + "\n"
    ret += pem_footer + "\n"

    return salt.utils.stringutils.to_bytes(ret, encoding="ascii")