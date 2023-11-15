    def __getattribute__(self, name):
        if name == 'next':
            raise AttributeError('next method should not be called')
        if name.startswith('__') and name.endswith('__'):
            return super(_Yes, self).__getattribute__(name)
        if name == 'accept':
            return super(_Yes, self).__getattribute__(name)
        return self