    def compute_encryption_key(self, password):
        # Algorithm 3.2
        password = (password + self.PASSWORD_PADDING)[:32]  # 1
        hash = md5.md5(password)  # 2
        hash.update(self.o)  # 3
        hash.update(struct.pack('<l', self.p))  # 4
        hash.update(self.docid[0])  # 5
        if self.r >= 4:
            if not self.encrypt_metadata:
                hash.update(b'\xff\xff\xff\xff')
        result = hash.digest()
        n = 5
        if self.r >= 3:
            n = self.length // 8
            for _ in range(50):
                result = md5.md5(result[:n]).digest()
        return result[:n]