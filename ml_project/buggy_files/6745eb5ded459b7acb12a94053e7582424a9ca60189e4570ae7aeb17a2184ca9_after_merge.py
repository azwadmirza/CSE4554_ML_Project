    def setup_dataframe(self, df, initialize_scales=False):
        """Prepare dataframe for fitting or predicting.

        Adds a time index and scales y. Creates auxiliary columns 't', 't_ix',
        'y_scaled', and 'cap_scaled'. These columns are used during both
        fitting and predicting.

        Parameters
        ----------
        df: pd.DataFrame with columns ds, y, and cap if logistic growth. Any
            specified additional regressors must also be present.
        initialize_scales: Boolean set scaling factors in self from df.

        Returns
        -------
        pd.DataFrame prepared for fitting or predicting.
        """
        if 'y' in df:
            df['y'] = pd.to_numeric(df['y'])
            if np.isinf(df['y'].values).any():
                raise ValueError('Found infinity in column y.')
        if df['ds'].dtype == np.int64:
            df['ds'] = df['ds'].astype(str)
        df['ds'] = pd.to_datetime(df['ds'])
        if df['ds'].isnull().any():
            raise ValueError('Found NaN in column ds.')
        for name in self.extra_regressors:
            if name not in df:
                raise ValueError(
                    'Regressor "{}" missing from dataframe'.format(name))
            df[name] = pd.to_numeric(df[name])
            if df[name].isnull().any():
                raise ValueError('Found NaN in column ' + name)
        for props in self.seasonalities.values():
            condition_name = props['condition_name']
            if condition_name is not None:
                if condition_name not in df:
                    raise ValueError(
                        'Condition "{}" missing from dataframe'.format(condition_name))
                if not df[condition_name].isin([True, False]).all():
                    raise ValueError('Found non-boolean in column ' + condition_name)
                df[condition_name] = df[condition_name].astype('bool')

        df = df.sort_values('ds')
        df.reset_index(inplace=True, drop=True)

        self.initialize_scales(initialize_scales, df)

        if self.logistic_floor:
            if 'floor' not in df:
                raise ValueError("Expected column 'floor'.")
        else:
            df['floor'] = 0
        if self.growth == 'logistic':
            if 'cap' not in df:
                raise ValueError(
                    "Capacities must be supplied for logistic growth in "
                    "column 'cap'"
                )
            if (df['cap'] <= df['floor']).any():
                raise ValueError(
                    'cap must be greater than floor (which defaults to 0).'
                )
            df['cap_scaled'] = (df['cap'] - df['floor']) / self.y_scale

        df['t'] = (df['ds'] - self.start) / self.t_scale
        if 'y' in df:
            df['y_scaled'] = (df['y'] - df['floor']) / self.y_scale

        for name, props in self.extra_regressors.items():
            df[name] = ((df[name] - props['mu']) / props['std'])
        return df