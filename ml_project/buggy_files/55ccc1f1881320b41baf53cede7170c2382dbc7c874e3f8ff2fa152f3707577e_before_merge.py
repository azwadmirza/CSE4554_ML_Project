    def decode(self, fx):
        ''' Converts the function code to the datastore to

        :param fx: The function we are working with
        :returns: one of [d(iscretes),i(inputs),h(oliding),c(oils)
        '''
        return self.__fx_mapper[fx]