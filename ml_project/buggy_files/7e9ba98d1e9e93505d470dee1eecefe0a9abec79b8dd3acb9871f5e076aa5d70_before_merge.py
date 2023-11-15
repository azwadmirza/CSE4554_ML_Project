    def set_result(self, result, separator=''):
        """Store the result (string) into the result key of the AMP
        if one_line is true then replace \n by separator
        """
        # self.configs['result'] = unicode(result, 'utf-8').encode('utf-8', errors='replace')
        if self.one_line():
            self.configs['result'] = str(result).replace('\n', separator)
        else:
            self.configs['result'] = str(result)