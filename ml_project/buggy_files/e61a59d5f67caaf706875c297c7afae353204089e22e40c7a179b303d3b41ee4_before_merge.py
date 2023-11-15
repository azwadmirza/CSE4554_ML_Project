    def commit(self, msg: str):
        self.repo.index.commit(msg)