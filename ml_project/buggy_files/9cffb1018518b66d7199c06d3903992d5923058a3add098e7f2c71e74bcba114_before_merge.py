    def __setitem__(self, key, v):
        key = self.convert_key(key)
        is_new = key not in self
        # early return to prevent unnecessary disk writes
        if not is_new and self[key] == v:
            return
        # recursively set db and path
        if isinstance(v, StoredDict):
            v.db = self.db
            v.path = self.path + [key]
            for k, vv in v.items():
                v[k] = vv
        # recursively convert dict to StoredDict.
        # _convert_dict is called breadth-first
        elif isinstance(v, dict):
            if self.db:
                v = self.db._convert_dict(self.path, key, v)
            v = StoredDict(v, self.db, self.path + [key])
        # convert_value is called depth-first
        if isinstance(v, dict) or isinstance(v, str):
            if self.db:
                v = self.db._convert_value(self.path, key, v)
        # set parent of StoredObject
        if isinstance(v, StoredObject):
            v.set_db(self.db)
        # set item
        dict.__setitem__(self, key, v)
        if self.db:
            self.db.set_modified(True)