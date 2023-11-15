    def __str__(self):
        value = ''
        if self.call_value:
            value = 'value:{}'.format(self.call_value)
        args = [str(a) for a in self.arguments]
        return '{} = new {}({}) {}'.format(self.lvalue, self.contract_name, ','.join(args), value)