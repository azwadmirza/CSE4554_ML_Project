    def run(self, creator, symlinks):
        bin_dir = self.dest(creator, self.src).parent
        dest = bin_dir / self.base
        method = self.method(symlinks)
        method(self.src, dest)
        make_exe(dest)
        for extra in self.aliases:
            link_file = bin_dir / extra
            if link_file.exists():
                link_file.unlink()
            if symlinks:
                link_file.symlink_to(self.base)
            else:
                copy(self.src, link_file)
            make_exe(link_file)