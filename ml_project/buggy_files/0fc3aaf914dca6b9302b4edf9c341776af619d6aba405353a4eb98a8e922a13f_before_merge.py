    async def connect(cls, path: Union[bytes, str], *args, **kwargs):
        db = cls()
        db.connection = await wrap_future(db.executor.submit(sqlite3.connect, path, *args, **kwargs))
        return db