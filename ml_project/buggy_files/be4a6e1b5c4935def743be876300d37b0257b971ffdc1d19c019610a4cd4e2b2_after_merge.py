    def __str__(self):
        txt = str(self._called)
        if self.call_gas or self.call_value:
            gas = f'gas: {self.call_gas}' if self.call_gas else ''
            value = f'value: {self.call_value}' if self.call_value else ''
            salt = f'salt: {self.call_salt}' if self.call_salt else ''
            if gas or value or salt:
                options = [gas, value, salt]
                txt += '{' + ','.join([o for o in options if o != '']) + '}'
        return txt + '(' + ','.join([str(a) for a in self._arguments]) + ')'