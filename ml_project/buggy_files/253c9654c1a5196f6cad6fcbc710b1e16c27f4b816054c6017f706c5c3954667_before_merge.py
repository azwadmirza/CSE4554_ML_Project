def generate_ssl_cert(target_file=None, overwrite=False, random=False, return_content=False, serial_number=None):
    # Note: Do NOT import "OpenSSL" at the root scope
    # (Our test Lambdas are importing this file but don't have the module installed)
    from OpenSSL import crypto

    if target_file and not overwrite and os.path.exists(target_file):
        key_file_name = '%s.key' % target_file
        cert_file_name = '%s.crt' % target_file
        return target_file, cert_file_name, key_file_name
    if random and target_file:
        if '.' in target_file:
            target_file = target_file.replace('.', '.%s.' % short_uid(), 1)
        else:
            target_file = '%s.%s' % (target_file, short_uid())

    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)

    # create a self-signed cert
    cert = crypto.X509()
    subj = cert.get_subject()
    subj.C = 'AU'
    subj.ST = 'Some-State'
    subj.L = 'Some-Locality'
    subj.O = 'LocalStack Org'  # noqa
    subj.OU = 'Testing'
    subj.CN = 'LocalStack'
    serial_number = serial_number or 1001
    cert.set_serial_number(serial_number)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    cert_file = StringIO()
    key_file = StringIO()
    cert_file.write(to_str(crypto.dump_certificate(crypto.FILETYPE_PEM, cert)))
    key_file.write(to_str(crypto.dump_privatekey(crypto.FILETYPE_PEM, k)))
    cert_file_content = cert_file.getvalue().strip()
    key_file_content = key_file.getvalue().strip()
    file_content = '%s\n%s' % (key_file_content, cert_file_content)
    if target_file:
        save_file(target_file, file_content)
        key_file_name = '%s.key' % target_file
        cert_file_name = '%s.crt' % target_file
        save_file(key_file_name, key_file_content)
        save_file(cert_file_name, cert_file_content)
        TMP_FILES.append(target_file)
        TMP_FILES.append(key_file_name)
        TMP_FILES.append(cert_file_name)
        if not return_content:
            return target_file, cert_file_name, key_file_name
    return file_content