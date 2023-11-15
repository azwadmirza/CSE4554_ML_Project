    def get_values(self, varname, burn=0, thin=1):
        """Get values from trace.

        Parameters
        ----------
        varname : str
        burn : int
        thin : int

        Returns
        -------
        A NumPy array
        """
        if burn is None:
            burn = 0
        if thin is None:
            thin = 1

        if burn < 0:
            burn = max(0, len(self) + burn)
        if thin < 1:
            raise ValueError('Only positive thin values are supported '
                             'in SQLite backend.')
        varname = str(varname)

        statement_args = {'chain': self.chain}
        if burn == 0 and thin == 1:
            action = 'select'
        elif thin == 1:
            action = 'select_burn'
            statement_args['burn'] = burn - 1
        elif burn == 0:
            action = 'select_thin'
            statement_args['thin'] = thin
        else:
            action = 'select_burn_thin'
            statement_args['burn'] = burn - 1
            statement_args['thin'] = thin

        self.db.connect()
        shape = (-1,) + self.var_shapes[varname]
        statement = TEMPLATES[action].format(table=varname)
        self.db.cursor.execute(statement, statement_args)
        values = _rows_to_ndarray(self.db.cursor)
        return values.reshape(shape)