    def get_index_of_file_in_files(self, file):
        if not self.metainfo:
            raise ValueError("TorrentDef does not have metainfo")
        info = self.metainfo[b'info']

        if file is not None and 'files' in info:
            for i in range(len(info['files'])):
                file_dict = info['files'][i]

                if 'path.utf-8' in file_dict:
                    intorrentpath = maketorrent.pathlist2filename(file_dict['path.utf-8'])
                else:
                    intorrentpath = maketorrent.pathlist2filename(file_dict['path'])

                if intorrentpath == file:
                    return i
            raise ValueError("File not found in torrent")
        else:
            raise ValueError("File not found in single-file torrent")