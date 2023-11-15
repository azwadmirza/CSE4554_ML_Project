        def cumprod(scol):
            @pandas_udf(returnType=self._kdf._sdf.schema[self.name].dataType)
            def negative_check(s):
                assert len(s) == 0 or ((s > 0) | (s.isnull())).all(), \
                    "values should be bigger than 0: %s" % s
                return s

            return F.sum(F.log(negative_check(scol)))