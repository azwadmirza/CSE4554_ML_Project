    def create_certificate(self, csr, issuer_options):
        """
        Creates a CFSSL certificate.

        :param csr:
        :param issuer_options:
        :return:
        """
        current_app.logger.info(
            "Requesting a new cfssl certificate with csr: {0}".format(csr)
        )

        url = "{0}{1}".format(current_app.config.get("CFSSL_URL"), "/api/v1/cfssl/sign")

        data = {"certificate_request": csr}
        data = json.dumps(data)

        try:
            hex_key = current_app.config.get("CFSSL_KEY")
            key = bytes.fromhex(hex_key)
        except (ValueError, NameError, TypeError):
            # unable to find CFSSL_KEY in config, continue using normal sign method
            pass
        else:
            data = data.encode()

            token = base64.b64encode(
                hmac.new(key, data, digestmod=hashlib.sha256).digest()
            )
            data = base64.b64encode(data)

            data = json.dumps(
                {"token": token.decode("utf-8"), "request": data.decode("utf-8")}
            )

            url = "{0}{1}".format(
                current_app.config.get("CFSSL_URL"), "/api/v1/cfssl/authsign"
            )
        response = self.session.post(
            url, data=data.encode(encoding="utf_8", errors="strict")
        )
        if response.status_code > 399:
            metrics.send("cfssl_create_certificate_failure", "counter", 1)
            raise Exception("Error creating cert. Please check your CFSSL API server")
        response_json = json.loads(response.content.decode("utf_8"))
        cert = response_json["result"]["certificate"]
        parsed_cert = parse_certificate(cert)
        metrics.send("cfssl_create_certificate_success", "counter", 1)
        return (
            cert,
            current_app.config.get("CFSSL_INTERMEDIATE"),
            parsed_cert.serial_number,
        )