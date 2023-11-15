    async def connect(cls, path: Union[bytes, str], *args, **kwargs):
        def _connect():
            return sqlite3.connect(path, *args, **kwargs)
        db = cls()
        db.connection = await asyncio.get_event_loop().run_in_executor(db.executor, _connect)
        return db