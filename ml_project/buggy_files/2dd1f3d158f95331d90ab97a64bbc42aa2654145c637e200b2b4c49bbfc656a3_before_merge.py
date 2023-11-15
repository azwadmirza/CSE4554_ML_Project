    def fetch(self):
        """Fetch the data from hddtemp daemon."""
        # Taking care of sudden deaths/stops of hddtemp daemon
        try:
            sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sck.connect((self.host, self.port))
            data = b''
            while True:
                received = sck.recv(4096)
                if not received:
                    break
                data += received
        except socket.error as e:
            logger.debug("Cannot connect to an HDDtemp server ({}:{} => {})".format(self.host, self.port, e))
            logger.debug("Disable the HDDtemp module. Use the --disable-hddtemp to hide the previous message.")
            if self.args is not None:
                self.args.disable_hddtemp = True
            data = ""
        finally:
            sck.close()
            if data != "":
                logger.debug("Received data from the HDDtemp server: {}".format(data))

        return data