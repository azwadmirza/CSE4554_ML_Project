    def do_show(self, arg):
        '''Show things on the network based on filters'''
        flags, arg = self.parser.get_flags(arg)
        action = arg.split()[0]
        func_calls = {'all': self.show_all,
                      'authors': self.show_authors,
                      'behavior': self.show_behavior,
                      'history': self.show_history,
                      'os': self.show_os,
                      'role': self.show_role,
                      'state': self.show_state,
                      'what': self.show_what,
                      'where': self.show_where}
        if action in func_calls:
            if action in ['all', 'authors']:
                func_calls[action](arg, flags)
            elif action in ['history', 'what', 'where']:
                if len(arg.split()) > 1:
                    func_calls[action](arg, flags)
                else:
                    print(action.upper() + ' <ID|IP|MAC>')
            else:
                valid = False
                for show_comm in self.show_completions:
                    if arg.startswith(show_comm):
                        valid = True
                        func_calls[action](arg, flags)
                if not valid:
                    print("Unknown command, try 'help show'")
        else:
            print("Unknown command, try 'help show'")