def get_hardcoded_cert_keystore(files):
    """Returns the hardcoded certificate keystore."""
    try:
        logger.info("Getting Hardcoded Certificates/Keystores")
        dat = ''
        certz = ''
        key_store = ''
        for file_name in files:
            ext = file_name.split('.')[-1]
            if re.search("cer|pem|cert|crt|pub|key|pfx|p12", ext):
                certz += escape(file_name) + "</br>"
            if re.search("jks|bks", ext):
                key_store += escape(file_name) + "</br>"
        if len(certz) > 1:
            dat += (
                "<tr><td>Certificate/Key Files Hardcoded inside the App.</td><td>" +
                certz +
                "</td><tr>"
            )
        if len(key_store) > 1:
            dat += "<tr><td>Hardcoded Keystore Found.</td><td>" + key_store + "</td><tr>"
        return dat
    except:
        PrintException("Getting Hardcoded Certificates/Keystores")