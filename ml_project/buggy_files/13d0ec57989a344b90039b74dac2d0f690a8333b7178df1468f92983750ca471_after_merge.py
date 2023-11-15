    def _handle_signal(self, handler, signal, interface_name=None, object_path=None, path_keyword=None):
        args = (handler, signal, interface_name or self.__interface_name, self.__bus_name,
                object_path or self.__obj_path)
        self.__bus.add_signal_receiver(*args, path_keyword=path_keyword)
        self.__signals.append(args)