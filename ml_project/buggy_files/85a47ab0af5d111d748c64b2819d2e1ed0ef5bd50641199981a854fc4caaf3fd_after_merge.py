    def __str__(self):
        options = ''
        if self.call_value:
            options = 'value:{} '.format(self.call_value)
        if self.call_salt:
            options += 'salt:{} '.format(self.call_salt)
        args = [str(a) for a in self.arguments]
        return '{} = new {}({}) {}'.format(self.lvalue, self.contract_name, ','.join(args), options)