    def _openssh_public_key_bytes(self, key):
        if isinstance(key, rsa.RSAPublicKey):
            public_numbers = key.public_numbers()
            return b"ssh-rsa " + base64.b64encode(
                ssh._ssh_write_string(b"ssh-rsa") +
                ssh._ssh_write_mpint(public_numbers.e) +
                ssh._ssh_write_mpint(public_numbers.n)
            )
        elif isinstance(key, dsa.DSAPublicKey):
            public_numbers = key.public_numbers()
            parameter_numbers = public_numbers.parameter_numbers
            return b"ssh-dss " + base64.b64encode(
                ssh._ssh_write_string(b"ssh-dss") +
                ssh._ssh_write_mpint(parameter_numbers.p) +
                ssh._ssh_write_mpint(parameter_numbers.q) +
                ssh._ssh_write_mpint(parameter_numbers.g) +
                ssh._ssh_write_mpint(public_numbers.y)
            )
        elif isinstance(key, ed25519.Ed25519PublicKey):
            raw_bytes = key.public_bytes(serialization.Encoding.Raw,
                                         serialization.PublicFormat.Raw)
            return b"ssh-ed25519 " + base64.b64encode(
                ssh._ssh_write_string(b"ssh-ed25519") +
                ssh._ssh_write_string(raw_bytes)
            )
        else:
            assert isinstance(key, ec.EllipticCurvePublicKey)
            public_numbers = key.public_numbers()
            try:
                curve_name = {
                    ec.SECP256R1: b"nistp256",
                    ec.SECP384R1: b"nistp384",
                    ec.SECP521R1: b"nistp521",
                }[type(public_numbers.curve)]
            except KeyError:
                raise ValueError(
                    "Only SECP256R1, SECP384R1, and SECP521R1 curves are "
                    "supported by the SSH public key format"
                )

            point = key.public_bytes(
                serialization.Encoding.X962,
                serialization.PublicFormat.UncompressedPoint
            )
            return b"ecdsa-sha2-" + curve_name + b" " + base64.b64encode(
                ssh._ssh_write_string(b"ecdsa-sha2-" + curve_name) +
                ssh._ssh_write_string(curve_name) +
                ssh._ssh_write_string(point)
            )