    def to_dict(self):
        layer_dict = {}
        pkg_list = []
        for pkg in self.__packages:
            pkg_list.append(pkg.to_dict())
            layer_dict.update({self.fs_hash: {'packages': pkg_list,
                                              'tar_file': self.__tar_file,
                                              'created_by': self.__created_by
                                              }})
        return layer_dict