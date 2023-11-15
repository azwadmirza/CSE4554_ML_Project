    def ThriftClientCall(function):
        # print type(function)
        funcName = function.__name__

        def wrapper(self, *args, **kwargs):
            # print('['+self.__host+':'+str(self.__port)+'] '
            #       '>>>>> ['+funcName+']')
            # before = datetime.datetime.now()
            self.transport.open()
            func = getattr(self.client, funcName)
            try:
                res = func(*args, **kwargs)
                return res
            except shared.ttypes.RequestFailed as reqfailure:
                if reqfailure.errorCode == shared.ttypes.ErrorCode.DATABASE:
                    print('Database error on server')
                    print(str(reqfailure.message))
                elif reqfailure.errorCode ==\
                        shared.ttypes.ErrorCode.AUTH_DENIED:
                    print('Authentication denied')
                    print(str(reqfailure.message))
                elif reqfailure.errorCode ==\
                        shared.ttypes.ErrorCode.UNAUTHORIZED:
                    print('Unauthorized to access')
                    print(str(reqfailure.message))
                else:
                    print('API call error: ' + funcName)
                    print(str(reqfailure))

            except TProtocolException as ex:
                print("Connection failed to {0}:{1}"
                      .format(self.__host, self.__port))
                print("Check if your CodeChecker server is running.")
            except socket.error as serr:
                print("Connection failed to {0}:{1}"
                      .format(self.__host, self.__port))
                errCause = os.strerror(serr.errno)
                print(errCause)
                print(str(serr))
                print("Check if your CodeChecker server is running.")
            finally:
                self.transport.close()

        return wrapper