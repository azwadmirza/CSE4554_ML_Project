def _parse_openssl_req(csr_filename):
    """
    Parses openssl command line output, this is a workaround for M2Crypto's
    inability to get them from CSR objects.
    """
    if not salt.utils.path.which("openssl"):
        raise salt.exceptions.SaltInvocationError("openssl binary not found in path")
    cmd = "openssl req -text -noout -in {}".format(csr_filename)

    output = __salt__["cmd.run_stdout"](cmd)

    output = re.sub(r": rsaEncryption", ":", output)
    output = re.sub(r"[0-9a-f]{2}:", "", output)

    return salt.utils.data.decode(salt.utils.yaml.safe_load(output))