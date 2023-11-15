    def __init__(self, globals, version, with_name=None):
        '''
        Constructor of the decorator 'with_deprecated'

        :param globals:
        :param version:
        :param with_name:
        :return:
        '''
        _DeprecationDecorator.__init__(self, globals, version)
        self._with_name = with_name