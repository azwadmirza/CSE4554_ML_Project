    def close(self):
        self.logger.debug('Closing server connection')

        self.client.close()

        if self.socket:
            self.logger.debug('Closing proxycommand socket connection')
            # https://github.com/paramiko/paramiko/issues/789  Avoid zombie ssh processes
            self.socket.process.kill()
            self.socket.process.poll()

        if self.sftp_client:
            self.sftp_client.close()

        if self.bastion_client:
            self.bastion_client.close()

        return True