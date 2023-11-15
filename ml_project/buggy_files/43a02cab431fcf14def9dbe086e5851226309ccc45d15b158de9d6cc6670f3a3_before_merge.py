    def get_real_file(self, file_path):
        """
        If the file is vault encrypted return a path to a temporary decrypted file
        If the file is not encrypted then the path is returned
        Temporary files are cleanup in the destructor
        """

        if not file_path or not isinstance(file_path, string_types):
            raise AnsibleParserError("Invalid filename: '%s'" % str(file_path))

        if not self.path_exists(file_path) or not self.is_file(file_path):
            raise AnsibleFileNotFound("the file_name '%s' does not exist, or is not readable" % file_path)

        if not self._vault:
            self._vault = VaultLib(password="")

        real_path = self.path_dwim(file_path)

        try:
            with open(to_bytes(real_path), 'rb') as f:
                data = f.read()
                if self._vault.is_encrypted(data):
                    # if the file is encrypted and no password was specified,
                    # the decrypt call would throw an error, but we check first
                    # since the decrypt function doesn't know the file name
                    if not self._vault_password:
                        raise AnsibleParserError("A vault password must be specified to decrypt %s" % file_path)

                    data = self._vault.decrypt(data, filename=real_path)
                    # Make a temp file
                    real_path = self._create_content_tempfile(data)
                    self._tempfiles.add(real_path)

            return real_path

        except (IOError, OSError) as e:
            raise AnsibleParserError("an error occurred while trying to read the file '%s': %s" % (real_path, str(e)))