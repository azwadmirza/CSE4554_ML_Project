def cert_info(app_dir, tools_dir):
    """Return certificate information."""
    try:
        logger.info("Reading Code Signing Certificate")
        cert = os.path.join(app_dir, 'META-INF/')
        cp_path = tools_dir + 'CertPrint.jar'
        files = [f for f in os.listdir(
            cert) if os.path.isfile(os.path.join(cert, f))]
        certfile = None
        dat = ''
        manidat = ''
        manifestfile = None
        if "CERT.RSA" in files:
            certfile = os.path.join(cert, "CERT.RSA")
        else:
            for file_name in files:
                if file_name.lower().endswith(".rsa"):
                    certfile = os.path.join(cert, file_name)
                elif file_name.lower().endswith(".dsa"):
                    certfile = os.path.join(cert, file_name)
        if certfile:
            args = [settings.JAVA_PATH + 'java', '-jar', cp_path, certfile]
            issued = 'good'
            dat = subprocess.check_output(args)
            unicode_output = str(dat, encoding="utf-8", errors="replace")
            dat = escape(unicode_output).replace('\n', '</br>')
        else:
            dat = 'No Code Signing Certificate Found!'
            issued = 'missing'
        if re.findall(r"Issuer: CN=Android Debug|Subject: CN=Android Debug", dat):
            issued = 'bad'
        if re.findall(r"\[SHA1withRSA\]", dat):
            issued = 'bad hash'
        if "MANIFEST.MF" in files:
            manifestfile = os.path.join(cert, "MANIFEST.MF")
        if manifestfile:
            with open(manifestfile,'r', encoding='utf-8') as manifile:
                manidat = manifile.read()
        sha256Digest = bool(re.findall(r"SHA-256-Digest", manidat))
        cert_dic = {
            'cert_info': dat,
            'issued': issued,
            'sha256Digest': sha256Digest
        }
        return cert_dic
    except:
        PrintException("Reading Code Signing Certificate")