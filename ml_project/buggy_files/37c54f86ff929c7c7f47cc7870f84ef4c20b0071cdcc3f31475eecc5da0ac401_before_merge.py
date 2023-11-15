    def calculateCategory(self, torrent_dict, display_name):
        # torrent_dict is the  dict of
        # a torrent file
        # return value: list of category the torrent belongs to

        files_list = []
        try:
            # the multi-files mode
            for ifiles in torrent_dict['info']["files"]:
                files_list.append((ifiles['path'][-1], ifiles['length'] / float(self.__size_change)))
        except KeyError:
            # single mode
            files_list.append(
                (torrent_dict['info']["name"], torrent_dict['info']['length'] / float(self.__size_change)))

        tracker = torrent_dict.get('announce')
        if not tracker:
            tracker = torrent_dict.get('announce-list', [['']])[0][0]

        comment = torrent_dict.get('comment')
        return self.calculateCategoryNonDict(files_list, display_name, tracker, comment)