    def environment_failure(self, error):
        '''
        Log environment failure for the daemon and exit with the error code.

        :param error:
        :return:
        '''
        logger.exception('Failed to create environment for {d_name}: {reason}'.format(
            d_name=self.__class__.__name__, reason=error.message))
        sys.exit(error.errno)