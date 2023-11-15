    def close(self):
        if self.socket:
            self.socket.close()

        if self.client:
            self.client.close()

        if self.sftp_client:
            self.sftp_client.close()

        if self.bastion_socket:
            self.bastion_socket.close()

        if self.bastion_client:
            self.bastion_client.close()

        return True