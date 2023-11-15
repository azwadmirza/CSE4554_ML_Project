    def get_certificate(self, host, port, timeout=3, retry_attempts: int = 3, retry_rate: int = 2,
                        current_attempt: int = 0):

        socket.setdefaulttimeout(timeout)  # Set Socket Timeout

        try:
            self.log.info(f"Fetching seednode {host}:{port} TLS certificate")
            seednode_certificate = ssl.get_server_certificate(addr=(host, port))

        except socket.timeout:
            if current_attempt == retry_attempts:
                message = f"No Response from seednode {host}:{port} after {retry_attempts} attempts"
                self.log.info(message)
                raise ConnectionRefusedError("No response from {}:{}".format(host, port))
            self.log.info(f"No Response from seednode {host}:{port}. Retrying in {retry_rate} seconds...")
            time.sleep(retry_rate)
            return self.get_certificate(host, port, timeout, retry_attempts, retry_rate, current_attempt + 1)

        else:
            certificate = x509.load_pem_x509_certificate(seednode_certificate.encode(),
                                                         backend=default_backend())
            return certificate