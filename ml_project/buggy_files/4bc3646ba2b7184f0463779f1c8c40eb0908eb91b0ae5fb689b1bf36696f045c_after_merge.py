    def _sql_message(self, as_unicode):
        util = _preloaded.preloaded.sql_util

        details = [self._message(as_unicode=as_unicode)]
        if self.statement:
            if not as_unicode and not compat.py3k:
                stmt_detail = "[SQL: %s]" % compat.safe_bytestring(
                    self.statement
                )
            else:
                stmt_detail = "[SQL: %s]" % self.statement
            details.append(stmt_detail)
            if self.params:
                if self.hide_parameters:
                    details.append(
                        "[SQL parameters hidden due to hide_parameters=True]"
                    )
                else:
                    params_repr = util._repr_params(
                        self.params, 10, ismulti=self.ismulti
                    )
                    details.append("[parameters: %r]" % params_repr)
        code_str = self._code_str()
        if code_str:
            details.append(code_str)
        return "\n".join(["(%s)" % det for det in self.detail] + details)