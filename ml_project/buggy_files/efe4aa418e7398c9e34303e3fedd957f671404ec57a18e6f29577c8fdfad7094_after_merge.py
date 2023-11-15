    def _process_msg(self, msg):
        if 'data' not in msg:
            return {}
        msg['data'] = dict(msg['data'])
        for col, values in msg['data'].items():
            if isinstance(values, dict):
                items = sorted([(int(k), v) for k, v in values.items()])
                values = [v for k, v in items]
            elif isinstance(values, list) and values and isinstance(values[0], dict):
                new_values = []
                for vals in values:
                    if isinstance(vals, dict):
                        vals = sorted([(int(k), v) for k, v in vals.items()])
                        vals = [v for k, v in vals]
                    new_values.append(vals)
                values = new_values
            elif any(isinstance(v, (int, float)) for v in values):
                values = [np.nan if v is None else v for v in values]
            msg['data'][col] = values
        return self._transform(msg)