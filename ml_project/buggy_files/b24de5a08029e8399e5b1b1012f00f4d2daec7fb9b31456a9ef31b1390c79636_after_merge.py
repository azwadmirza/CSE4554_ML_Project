    def summary(self):
        """
        This returns the formatted result of the OLS computation
        """
        template = """
%(bannerTop)s

Formula: Y ~ %(formula)s

Number of Observations:         %(nobs)d
Number of Degrees of Freedom:   %(df)d

R-squared:     %(r2)10.4f
Adj R-squared: %(r2_adj)10.4f

Rmse:          %(rmse)10.4f

F-stat %(f_stat_shape)s: %(f_stat)10.4f, p-value: %(f_stat_p_value)10.4f

Degrees of Freedom: model %(df_model)d, resid %(df_resid)d

%(bannerCoef)s
%(coef_table)s
%(bannerEnd)s
"""
        coef_table = self._coef_table

        results = self._results

        f_stat = results['f_stat']

        bracketed = ['<%s>' %str(c) for c in results['beta'].index]

        formula = StringIO()
        formula.write(bracketed[0])
        tot = len(bracketed[0])
        line = 1
        for coef in bracketed[1:]:
            tot = tot + len(coef) + 3

            if tot // (68 * line):
                formula.write('\n' + ' ' * 12)
                line += 1

            formula.write(' + ' + coef)

        params = {
            'bannerTop' : scom.banner('Summary of Regression Analysis'),
            'bannerCoef' : scom.banner('Summary of Estimated Coefficients'),
            'bannerEnd' : scom.banner('End of Summary'),
            'formula' : formula.getvalue(),
            'r2' : results['r2'],
            'r2_adj' : results['r2_adj'],
            'nobs' : results['nobs'],
            'df'  : results['df'],
            'df_model'  : results['df_model'],
            'df_resid'  : results['df_resid'],
            'coef_table' : coef_table,
            'rmse' : results['rmse'],
            'f_stat' : f_stat['f-stat'],
            'f_stat_shape' : '(%d, %d)' % (f_stat['DF X'], f_stat['DF Resid']),
            'f_stat_p_value' : f_stat['p-value'],
        }

        return template % params