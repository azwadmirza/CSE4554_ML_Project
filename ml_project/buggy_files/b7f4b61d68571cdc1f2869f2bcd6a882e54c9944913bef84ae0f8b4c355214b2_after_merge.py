    def find_git_working_directory(self, directory):
        '''Return the git working directory, starting at directory.'''
        while directory:
            if g.os_path_exists(g.os_path_finalize_join(directory, '.git')):
                return directory
            path2 = g.os_path_finalize_join(directory, '..')
            if path2 == directory:
                break
            directory = path2
        return None