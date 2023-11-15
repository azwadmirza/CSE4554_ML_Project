    def set_result(self, result, separator=''):
        """Store the result (string) into the result key of the AMP
        if one_line is true then replace \n by separator
        """
        if self.one_line():
            self.configs['result'] = u(result).replace('\n', separator)
        else:
            self.configs['result'] = u(result)