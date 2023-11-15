    def run(self):
        results = None
        if self.args.action in ['start', 'restart', 'stop', 'status']:
            if self.args.parameter:
                method_name = "bot_" + self.args.action
                call_method = getattr(self, method_name)
                results = call_method(self.args.parameter)
            else:
                method_name = "botnet_" + self.args.action
                call_method = getattr(self, method_name)
                results = call_method()
        elif self.args.action == 'run':
            if self.args.parameter and len(self.args.parameter) == 1:
                self.bot_run(self.args.parameter[0])
            else:
                print("Exactly one bot-id must be given for run.")
                exit(2)
        elif self.args.action == 'list':
            if self.args.parameter[0] not in ['bots', 'queues']:
                print("Second argument must be 'bots' or 'queues'.")
                exit(2)
            method_name = "list_" + self.args.parameter[0]
            call_method = getattr(self, method_name)
            results = call_method()
        elif self.args.action == 'log':
            if not self.args.parameter:
                print("You must give parameters for 'log'.")
                exit(2)
            results = self.read_log(*self.args.parameter)
        elif self.args.action == 'clear':
            if not self.args.parameter:
                print("Queue name not given.")
                exit(2)
            results = self.clear_queue(self.args.parameter)

        if self.args.type == 'json':
            print(json.dumps(results))