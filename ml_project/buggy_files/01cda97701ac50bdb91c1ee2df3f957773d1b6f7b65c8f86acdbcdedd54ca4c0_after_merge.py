    def do_task(self, arg):
        '''Perform task to things on the network'''
        # TODO
        flags, arg = self.parser.get_flags(arg)
        if arg:
            action = arg.split()[0]
            func_calls = {'clear': self.task_clear,
                          'collect': self.task_collect,
                          'ignore': self.task_ignore,
                          'remove': self.task_remove,
                          'set': self.task_set}
            if action in func_calls:
                if len(arg.split()) > 1:
                    func_calls[action](arg, flags)
                else:
                    print(action.upper() + ' <ID|IP|MAC>')
            else:
                print("Unknown command, try 'help task'")
        else:
            self.help_task()