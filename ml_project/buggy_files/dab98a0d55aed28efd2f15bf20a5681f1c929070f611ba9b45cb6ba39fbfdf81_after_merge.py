def get_server(protocol, authenticated=False):
    if protocol == "imap":
        hostname, port = extract_host_port(app.config['IMAP_ADDRESS'], 143)
    elif protocol == "pop3":
        hostname, port = extract_host_port(app.config['POP3_ADDRESS'], 110)
    elif protocol == "smtp":
        if authenticated:
            hostname, port = extract_host_port(app.config['AUTHSMTP_ADDRESS'], 10025)
        else:
            hostname, port = extract_host_port(app.config['SMTP_ADDRESS'], 25)
    return hostname, port