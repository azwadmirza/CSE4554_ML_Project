        def _check_basicConstraints(extensions):
            bc_ext = _find_extension(extensions, cryptography.x509.BasicConstraints)
            current_ca = bc_ext.value.ca if bc_ext else False
            current_path_length = bc_ext.value.path_length if bc_ext else None
            ca, path_length = crypto_utils.cryptography_get_basic_constraints(self.basicConstraints)
            # Check CA flag
            if ca != current_ca:
                return False
            # Check path length
            if path_length != current_path_length:
                return False
            # Check criticality
            if self.basicConstraints:
                if bc_ext.critical != self.basicConstraints_critical:
                    return False
            return True