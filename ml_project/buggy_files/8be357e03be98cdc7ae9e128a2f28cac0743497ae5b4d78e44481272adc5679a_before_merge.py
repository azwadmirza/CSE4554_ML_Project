    def get(self, checksum_address: str, federated_only: bool, certificate_only: bool = False):
        if certificate_only is True:
            certificate = self.__read_tls_public_certificate(checksum_address=checksum_address)
            return certificate
        metadata_path = self.__generate_metadata_filepath(checksum_address=checksum_address)
        node = self.__read_metadata(filepath=metadata_path,
                                    registry=self.registry,
                                    federated_only=federated_only)  # TODO: 466
        return node