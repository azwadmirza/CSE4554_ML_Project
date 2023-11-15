    def get_options(self):
        opts = {'cpp_std' : coredata.UserComboOption('cpp_std', 'C++ language standard to use',
                                                     ['none', 'c++03', 'c++11', 'c++14', 'c++1z',
                                                      'gnu++03', 'gnu++11', 'gnu++14', 'gnu++1z'],
                                                     'none'),
                'cpp_debugstl': coredata.UserBooleanOption('cpp_debugstl',
                                                           'STL debug mode',
                                                           False)}
        if self.gcc_type == GCC_MINGW:
            opts.update({
                'cpp_winlibs': coredata.UserStringArrayOption('cpp_winlibs', 'Standard Win libraries to link against',
                                                              gnu_winlibs),
                })
        return opts