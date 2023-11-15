    def execute(self):
        try:
            logger.debug("Passive hunter is attempting to get server certificate")
            addr = (str(self.event.host), self.event.port)
            cert = ssl.get_server_certificate(addr)
        except ssl.SSLError:
            # If the server doesn't offer SSL on this port we won't get a certificate
            return
        c = cert.strip(ssl.PEM_HEADER).strip(ssl.PEM_FOOTER)
        certdata = base64.decodebytes(c)
        emails = re.findall(email_pattern, certdata)
        for email in emails:
            self.publish_event(CertificateEmail(email=email))