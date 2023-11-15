    def __str__(self):
        value = ''
        gas = ''
        args = [str(a) for a in self.arguments]
        if self.call_value:
            value = 'value:{}'.format(self.call_value)
        if self.call_gas:
            gas = 'gas:{}'.format(self.call_gas)
        if not self.lvalue:
            lvalue = ''
        elif isinstance(self.lvalue.type, (list,)):
            lvalue = '{}({}) = '.format(self.lvalue, ','.join(str(x) for x in self.lvalue.type))
        else:
            lvalue = '{}({}) = '.format(self.lvalue, self.lvalue.type)
        txt = '{}INTERNAL_DYNAMIC_CALL {}({}) {} {}'
        return txt.format(lvalue,
                          self.function.name,
                          ','.join(args),
                          value,
                          gas)