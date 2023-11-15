    def init(self, clean=False):
        cursor = None
        try:
            cursor = self.connection.cursor()
            if clean:
                cursor.execute("drop table if exists %s" % REMOTES_USER_TABLE)
            cursor.execute("create table if not exists %s "
                           "(remote_url TEXT UNIQUE, user TEXT, token TEXT)" % REMOTES_USER_TABLE)
        except Exception as e:
            message = "Could not initialize local sqlite database"
            raise ConanException(message, e)
        finally:
            if cursor:
                cursor.close()