    def transform_parameter(self):
        # Depreciated placeholders:
        # - $[taskcat_gets3contents]
        # - $[taskcat_geturl]
        for param_name, param_value in self._param_dict.items():
            if isinstance(param_value, list):
                _results_list = []
                _nested_param_dict = {}
                for idx, value in enumerate(param_value):
                    _nested_param_dict[idx] = value
                nested_pg = ParamGen(
                    _nested_param_dict,
                    self.bucket_name,
                    self.region,
                    self._boto_client,
                    self.az_excludes,
                )
                nested_pg.transform_parameter()
                for result_value in nested_pg.results.values():
                    _results_list.append(result_value)
                self.param_value = _results_list
                self.results.update({param_name: _results_list})
                continue

            # Setting the instance variables to reflect key/value pair we're working on.
            self.param_name = param_name
            self.param_value = param_value

            # Convert from bytes to string.
            self.convert_to_str()

            # $[taskcat_random-numbers]
            self._regex_replace_param_value(self.RE_GENNUMB, self._gen_rand_num(20))

            # $[taskcat_random-string]
            self._regex_replace_param_value(self.RE_GENRANDSTR, self._gen_rand_str(20))

            # $[taskcat_autobucket]
            self._regex_replace_param_value(
                self.RE_GENAUTOBUCKET, self._gen_autobucket()
            )

            # $[taskcat_genpass_X]
            self._gen_password_wrapper(self.RE_GENPW, self.RE_PWTYPE, self.RE_COUNT)

            # $[taskcat_ge[nt]az_#]
            self._gen_az_wrapper(self.RE_GENAZ, self.RE_COUNT)

            # $[taskcat_ge[nt]singleaz_#]
            self._gen_single_az_wrapper(self.RE_GENAZ_SINGLE)

            # $[taskcat_getkeypair]
            self._regex_replace_param_value(self.RE_QSKEYPAIR, "cikey")

            # $[taskcat_getlicensebucket]
            self._regex_replace_param_value(self.RE_QSLICBUCKET, "override_this")

            # $[taskcat_getmediabucket]
            self._regex_replace_param_value(self.RE_QSMEDIABUCKET, "override_this")

            # $[taskcat_getlicensecontent]
            self._get_license_content_wrapper(self.RE_GETLICCONTENT)

            # $[taskcat_getpresignedurl]
            self._get_license_content_wrapper(self.RE_GETPRESIGNEDURL)

            # $[taskcat_getval_X]
            self._getval_wrapper(self.RE_GETVAL)

            # $[taskcat_genuuid]
            self._regex_replace_param_value(self.RE_GENUUID, self._gen_uuid())
            self.results.update({self.param_name: self.param_value})