    def from_json(cls, data):
        data_path = data_manager.cog_data_path()
        # noinspection PyTypeChecker
        return Repo(data['name'], data['url'], data['branch'],
                    data_path / Path(*data['folder_path']),
                    tuple([Installable.from_json(m) for m in data['available_modules']]))