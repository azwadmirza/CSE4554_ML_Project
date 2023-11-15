    def commit(self, msg: str):
        from dulwich.porcelain import commit

        commit(self.root_dir, message=msg)