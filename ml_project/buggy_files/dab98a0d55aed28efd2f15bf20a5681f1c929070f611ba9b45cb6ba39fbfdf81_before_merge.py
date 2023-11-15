def get_server(protocol, authenticated=False):
    if protocol == "imap":
        hostname, port = extract_host_port(app.config['HOST_IMAP'], 143)
    elif protocol == "pop3":
        hostname, port = extract_host_port(app.config['HOST_POP3'], 110)
    elif protocol == "smtp":
        if authenticated:
            hostname, port = extract_host_port(app.config['HOST_AUTHSMTP'], 10025)
        else:
            hostname, port = extract_host_port(app.config['HOST_SMTP'], 25)
    return hostname, port