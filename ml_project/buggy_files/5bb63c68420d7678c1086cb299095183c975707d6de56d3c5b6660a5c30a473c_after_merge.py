    def verify_tops(self, tops):
        '''
        Verify the contents of the top file data
        '''
        errors = []
        if not isinstance(tops, dict):
            errors.append('Top data was not formed as a dict')
            # No further checks will work, bail out
            return errors
        for env, matches in tops.items():
            if env == 'include':
                continue
            if not isinstance(env, string_types):
                err = ('Environment {0} in top file is not formed as a '
                       'string').format(env)
                errors.append(err)
            if env == '':
                errors.append('Empty environment statement in top file')
            if not isinstance(matches, dict):
                err = ('The top file matches for environment {0} are not '
                       'laid out as a dict').format(env)
                errors.append(err)
            for slsmods in matches.values():
                if not isinstance(slsmods, list):
                    errors.append('Malformed topfile (state declarations not '
                                  'formed as a list)')
                    continue
                for slsmod in slsmods:
                    if isinstance(slsmod, dict):
                        # This value is a match option
                        for val in slsmod.values():
                            if not val:
                                err = ('Improperly formatted top file matcher '
                                       'in environment {0}: {1} file'.format(
                                           slsmod,
                                           val
                                           )
                                       )
                                errors.append(err)
                    elif isinstance(slsmod, string_types):
                        # This is a sls module
                        if not slsmod:
                            err = ('Environment {0} contains an empty sls '
                                   'index').format(env)
                            errors.append(err)

        return errors