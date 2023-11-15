    def run(self, args, config):
        library = _get_library(args, config)
        prompt = '\nAre you sure you want to clear the library? [y/N] '

        if compat.input(prompt).lower() != 'y':
            print('Clearing library aborted.')
            return 0

        if library.clear():
            print('Library successfully cleared.')
            return 0

        print('Unable to clear library.')
        return 1