    def decrypt_str(self, content, key, salt):
        # content contains the gcm tag and salt_explicit in plaintext
        salt_explicit, gcm_tag = struct.unpack_from('!q16s', content)
        cipher = Cipher(algorithms.AES(key),
                        modes.GCM(initialization_vector=self._bulid_iv(salt, salt_explicit), tag=gcm_tag),
                        backend=default_backend()
                        ).decryptor()
        return cipher.update(content[24:]) + cipher.finalize()