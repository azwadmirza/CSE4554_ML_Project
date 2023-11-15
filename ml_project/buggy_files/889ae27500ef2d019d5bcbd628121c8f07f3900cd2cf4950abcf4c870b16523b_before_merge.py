    def print_paths(finder):
        ''' Returns a string suitable for printing of the search path '''

        # Uses a list to get the order right
        ret = []
        for i in finder._get_paths(subdirs=False):
            if i not in ret:
                ret.append(i)
        return os.pathsep.join(ret)