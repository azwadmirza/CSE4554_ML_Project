def _parse_openssl_crl(crl_filename):
    """
    Parses openssl command line output, this is a workaround for M2Crypto's
    inability to get them from CSR objects.
    """
    if not salt.utils.path.which("openssl"):
        raise salt.exceptions.SaltInvocationError("openssl binary not found in path")
    cmd = "openssl crl -text -noout -in {}".format(crl_filename)

    output = __salt__["cmd.run_stdout"](cmd)

    crl = {}
    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("Version "):
            crl["Version"] = line.replace("Version ", "")
        if line.startswith("Signature Algorithm: "):
            crl["Signature Algorithm"] = line.replace("Signature Algorithm: ", "")
        if line.startswith("Issuer: "):
            line = line.replace("Issuer: ", "")
            subject = {}
            for sub_entry in line.split("/"):
                if "=" in sub_entry:
                    sub_entry = sub_entry.split("=")
                    subject[sub_entry[0]] = sub_entry[1]
            crl["Issuer"] = subject
        if line.startswith("Last Update: "):
            crl["Last Update"] = line.replace("Last Update: ", "")
            last_update = datetime.datetime.strptime(
                crl["Last Update"], "%b %d %H:%M:%S %Y %Z"
            )
            crl["Last Update"] = last_update.strftime("%Y-%m-%d %H:%M:%S")
        if line.startswith("Next Update: "):
            crl["Next Update"] = line.replace("Next Update: ", "")
            next_update = datetime.datetime.strptime(
                crl["Next Update"], "%b %d %H:%M:%S %Y %Z"
            )
            crl["Next Update"] = next_update.strftime("%Y-%m-%d %H:%M:%S")
        if line.startswith("Revoked Certificates:"):
            break

    if "No Revoked Certificates." in output:
        crl["Revoked Certificates"] = []
        return crl

    output = output.split("Revoked Certificates:")[1]
    output = output.split("Signature Algorithm:")[0]

    rev = []
    for revoked in output.split("Serial Number: "):
        if not revoked.strip():
            continue

        rev_sn = revoked.split("\n")[0].strip()
        revoked = rev_sn + ":\n" + "\n".join(revoked.split("\n")[1:])
        rev_yaml = salt.utils.data.decode(salt.utils.yaml.safe_load(revoked))
        for rev_values in rev_yaml.values():
            if "Revocation Date" in rev_values:
                rev_date = datetime.datetime.strptime(
                    rev_values["Revocation Date"], "%b %d %H:%M:%S %Y %Z"
                )
                rev_values["Revocation Date"] = rev_date.strftime("%Y-%m-%d %H:%M:%S")

        rev.append(rev_yaml)

    crl["Revoked Certificates"] = rev

    return crl