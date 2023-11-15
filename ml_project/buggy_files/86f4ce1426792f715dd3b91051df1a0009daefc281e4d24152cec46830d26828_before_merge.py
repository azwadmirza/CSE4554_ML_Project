    def poke(self, context):
        return self.is_keys_unchanged(set(self.hook.list_keys(self.bucket, prefix=self.prefix)))