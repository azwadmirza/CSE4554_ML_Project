    def run(self, terms, variables, **kwargs):

        def _raise_terms_error(msg=""):
            raise AnsibleError(
                "subelements lookup expects a list of two or three items, "
                + msg)
        terms = listify_lookup_plugin_terms(terms, variables, loader=self._loader)
        terms[0] = listify_lookup_plugin_terms(terms[0], variables, loader=self._loader)

        # check lookup terms - check number of terms
        if not isinstance(terms, list) or not 2 <= len(terms) <= 3:
            _raise_terms_error()

        # first term should be a list (or dict), second a string holding the subkey
        if not isinstance(terms[0], (list, dict)) or not isinstance(terms[1], basestring):
            _raise_terms_error("first a dict or a list, second a string pointing to the subkey")
        subelements = terms[1].split(".")

        if isinstance(terms[0], dict):  # convert to list:
            if terms[0].get('skipped', False) is not False:
                # the registered result was completely skipped
                return []
            elementlist = []
            for key in terms[0].iterkeys():
                elementlist.append(terms[0][key])
        else:
            elementlist = terms[0]

        # check for optional flags in third term
        flags = {}
        if len(terms) == 3:
            flags = terms[2]
        if not isinstance(flags, dict) and not all([isinstance(key, basestring) and key in FLAGS for key in flags]):
            _raise_terms_error("the optional third item must be a dict with flags %s" % FLAGS)

        # build_items
        ret = []
        for item0 in elementlist:
            if not isinstance(item0, dict):
                raise AnsibleError("subelements lookup expects a dictionary, got '%s'" % item0)
            if item0.get('skipped', False) is not False:
                # this particular item is to be skipped
                continue

            skip_missing = boolean(flags.get('skip_missing', False))
            subvalue = item0
            lastsubkey = False
            sublist = []
            for subkey in subelements:
                if subkey == subelements[-1]:
                    lastsubkey = True
                if not subkey in subvalue:
                    if skip_missing:
                        continue
                    else:
                        raise AnsibleError("could not find '%s' key in iterated item '%s'" % (subkey, subvalue))
                if not lastsubkey:
                    if not isinstance(subvalue[subkey], dict):
                        if skip_missing:
                            continue
                        else:
                            raise AnsibleError("the key %s should point to a dictionary, got '%s'" % (subkey, subvalue[subkey]))
                    else:
                        subvalue = subvalue[subkey]
                else:  # lastsubkey
                    if not isinstance(subvalue[subkey], list):
                        raise AnsibleError("the key %s should point to a list, got '%s'" % (subkey, subvalue[subkey]))
                    else:
                        sublist = subvalue.pop(subkey, [])
            for item1 in sublist:
                ret.append((item0, item1))

        return ret