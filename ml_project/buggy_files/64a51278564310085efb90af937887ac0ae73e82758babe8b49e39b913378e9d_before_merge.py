    def from_json(cls, data):
        # noinspection PyTypeChecker
        return Repo(data['name'], data['url'], data['branch'],
                    Path.cwd() / Path(*data['folder_path']),
                    tuple([Installable.from_json(m) for m in data['available_modules']]))