    def _mine_get(self, load, skip_verify=False):
        '''
        Gathers the data from the specified minions' mine
        '''
        if not skip_verify:
            if any(key not in load for key in ('id', 'tgt', 'fun')):
                return {}

        if isinstance(load['fun'], six.string_types):
            functions = list(set(load['fun'].split(',')))
            _ret_dict = len(functions) > 1
        elif isinstance(load['fun'], list):
            functions = load['fun']
            _ret_dict = True
        else:
            return {}

        functions_allowed = []

        if 'mine_get' in self.opts:
            # If master side acl defined.
            if not isinstance(self.opts['mine_get'], dict):
                return {}
            perms = set()
            for match in self.opts['mine_get']:
                if re.match(match, load['id']):
                    if isinstance(self.opts['mine_get'][match], list):
                        perms.update(self.opts['mine_get'][match])
            for fun in functions:
                if any(re.match(perm, fun) for perm in perms):
                    functions_allowed.append(fun)
            if not functions_allowed:
                return {}
        else:
            functions_allowed = functions

        ret = {}
        if not salt.utils.verify.valid_id(self.opts, load['id']):
            return ret

        expr_form = load.get('expr_form')
        # keep both expr_form and tgt_type to ensure
        # comptability between old versions of salt
        if expr_form is not None and 'tgt_type' not in load:
            match_type = expr_form
        else:
            match_type = load.get('tgt_type', 'glob')
        if match_type.lower() == 'pillar':
            match_type = 'pillar_exact'
        if match_type.lower() == 'compound':
            match_type = 'compound_pillar_exact'
        checker = salt.utils.minions.CkMinions(self.opts)
        _res = checker.check_minions(
                load['tgt'],
                match_type,
                greedy=False
                )
        minions = _res['minions']
        minion_side_acl = {}  # Cache minion-side ACL
        for minion in minions:
            mine_data = self.cache.fetch('minions/{0}'.format(minion), 'mine')
            if not isinstance(mine_data, dict):
                continue
            for function in functions_allowed:
                if function not in mine_data:
                    continue
                mine_entry = mine_data[function]
                mine_result = mine_data[function]
                if isinstance(mine_entry, dict) and salt.utils.mine.MINE_ITEM_ACL_ID in mine_entry:
                    mine_result = mine_entry[salt.utils.mine.MINE_ITEM_ACL_DATA]
                    # Check and fill minion-side ACL cache
                    if function not in minion_side_acl.get(minion, {}):
                        if 'allow_tgt' in mine_entry:
                            # Only determine allowed targets if any have been specified.
                            # This prevents having to add a list of all minions as allowed targets.
                            get_minion = checker.check_minions(
                                         mine_entry['allow_tgt'],
                                         mine_entry.get('allow_tgt_type', 'glob'))['minions']
                            # the minion in allow_tgt does not exist
                            if not get_minion:
                                continue
                            salt.utils.dictupdate.set_dict_key_value(
                                minion_side_acl,
                                '{}:{}'.format(minion, function),
                                get_minion
                           )
                if salt.utils.mine.minion_side_acl_denied(minion_side_acl, minion, function, load['id']):
                    continue
                if _ret_dict:
                    ret.setdefault(function, {})[minion] = mine_result
                else:
                    # There is only one function in functions_allowed.
                    ret[minion] = mine_result
        return ret