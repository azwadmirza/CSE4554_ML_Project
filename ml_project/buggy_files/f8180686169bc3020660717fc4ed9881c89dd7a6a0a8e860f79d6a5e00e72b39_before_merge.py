    def create_storage(self, path):
        if os.path.exists(path):
            raise Exception('file already exists at path')
        if not self.pw_args:
            return
        pw_args = self.pw_args
        self.pw_args = None  # clean-up so that it can get GC-ed
        storage = WalletStorage(path)
        if pw_args.encrypt_storage:
            storage.set_password(pw_args.password, enc_version=pw_args.storage_enc_version)
        db = WalletDB('', manual_upgrades=False)
        db.set_keystore_encryption(bool(pw_args.password) and pw_args.encrypt_keystore)
        for key, value in self.data.items():
            db.put(key, value)
        db.load_plugins()
        db.write(storage)
        return storage, db