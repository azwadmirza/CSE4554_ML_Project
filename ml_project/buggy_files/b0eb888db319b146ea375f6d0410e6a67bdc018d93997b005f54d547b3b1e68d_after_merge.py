    def all(self, federated_only: bool, certificates_only: bool = False) -> Set[Union[Any, Certificate]]:
        filenames = os.listdir(self.certificates_dir if certificates_only else self.metadata_dir)
        self.log.info("Found {} known node metadata files at {}".format(len(filenames), self.metadata_dir))

        known_certificates = set()
        if certificates_only:
            for filename in filenames:
                certificate = self.__read_tls_public_certificate(os.path.join(self.certificates_dir, filename))
                known_certificates.add(certificate)
            return known_certificates

        else:
            known_nodes = set()
            for filename in filenames:
                metadata_path = os.path.join(self.metadata_dir, filename)
                node = self.__read_metadata(filepath=metadata_path, federated_only=federated_only)  # TODO: 466
                known_nodes.add(node)
            return known_nodes