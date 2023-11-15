    def executescript(self, script: str) -> Awaitable:
        return self.run(lambda conn: conn.executescript(script))