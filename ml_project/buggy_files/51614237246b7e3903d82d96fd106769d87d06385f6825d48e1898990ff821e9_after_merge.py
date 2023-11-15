    def listdir(self, path=None):
        path = normalize_storage_path(path)
        sep = '_' if path == '' else '/'
        keys = self.cursor.execute(
            '''
            SELECT DISTINCT SUBSTR(m, 0, INSTR(m, "/")) AS l FROM (
                SELECT LTRIM(SUBSTR(k, LENGTH(?) + 1), "/") || "/" AS m
                FROM zarr WHERE k LIKE (? || "{sep}%")
            ) ORDER BY l ASC
            '''.format(sep=sep),
            (path, path)
        )
        keys = list(map(operator.itemgetter(0), keys))
        return keys