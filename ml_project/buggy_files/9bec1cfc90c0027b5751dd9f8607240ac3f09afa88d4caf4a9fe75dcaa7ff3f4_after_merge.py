    def wheel_check(self, auth_list, fun):
        '''
        Check special API permissions
        '''
        if not auth_list:
            return False
        comps = fun.split('.')
        if len(comps) != 2:
            return False
        mod = comps[0]
        fun = comps[1]
        for ind in auth_list:
            if isinstance(ind, six.string_types):
                if ind.startswith('@') and ind[1:] == mod:
                    return True
                if ind == '@wheel':
                    return True
                if ind == '@wheels':
                    return True
            elif isinstance(ind, dict):
                if len(ind) != 1:
                    continue
                valid = next(six.iterkeys(ind))
                if valid.startswith('@') and valid[1:] == mod:
                    if isinstance(ind[valid], six.string_types):
                        if self.match_check(ind[valid], fun):
                            return True
                    elif isinstance(ind[valid], list):
                        for regex in ind[valid]:
                            if self.match_check(regex, fun):
                                return True
        return False