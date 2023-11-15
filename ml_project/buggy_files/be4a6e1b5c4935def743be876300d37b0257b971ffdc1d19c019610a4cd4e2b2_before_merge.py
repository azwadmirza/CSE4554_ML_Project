    def __str__(self):
        txt = str(self._called)
        if self.call_gas or self.call_value:
            gas = f'gas: {self.call_gas}' if self.call_gas else ''
            value = f'value: {self.call_value}' if self.call_value else ''
            if gas and value:
                txt += '{' + f'{gas}, {value}' + '}'
            elif gas:
                txt += '{' + f'{gas}' + '}'
            else:
                txt += '{' + f'{value}' + '}'
        return txt + '(' + ','.join([str(a) for a in self._arguments]) + ')'