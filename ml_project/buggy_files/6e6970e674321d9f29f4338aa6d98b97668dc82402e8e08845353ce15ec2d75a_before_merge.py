    def _special_cases(self, cmd, outside):
        break_flag = False
        continue_flag = False
        args = parse_quotes(cmd)
        cmd_stripped = cmd.strip()

        if not cmd_stripped and cmd:
            # add scope if there are only spaces
            cmd = self.default_command + " " + cmd
        elif cmd_stripped == "quit" or cmd_stripped == "exit":
            break_flag = True
        elif cmd_stripped == "clear-history":
            continue_flag = True
            self.reset_history()
        elif cmd_stripped == CLEAR_WORD:
            outside = True
            cmd = CLEAR_WORD
        elif cmd_stripped[0] == SELECT_SYMBOL['outside']:
            cmd = cmd_stripped[1:]
            outside = True
            if cmd.strip() and cmd.split()[0] == 'cd':
                self.handle_cd(parse_quotes(cmd))
                continue_flag = True
            telemetry.track_outside_gesture()

        elif cmd_stripped[0] == SELECT_SYMBOL['exit_code']:
            meaning = "Success" if self.last_exit == 0 else "Failure"

            print(meaning + ": " + str(self.last_exit), file=self.output)
            continue_flag = True
            telemetry.track_exit_code_gesture()
        elif SELECT_SYMBOL['query'] in cmd_stripped and self.last and self.last.result:
            continue_flag = self.handle_jmespath_query(args)
            telemetry.track_query_gesture()

        elif args[0] == '--version' or args[0] == '-v':
            try:
                continue_flag = True
                self.cli_ctx.show_version()
            except SystemExit:
                pass
        elif SELECT_SYMBOL['example'] in cmd:
            cmd, continue_flag = self.handle_example(cmd, continue_flag)
            telemetry.track_ran_tutorial()
        elif SELECT_SYMBOL['scope'] == cmd_stripped[0:2]:
            continue_flag, cmd = self.handle_scoping_input(continue_flag, cmd, cmd_stripped)
            telemetry.track_scope_changes()
        else:
            # not a special character; add scope and remove 'az'
            if self.default_command:
                cmd = self.default_command + " " + cmd
            elif cmd.split(' ', 1)[0].lower() == 'az':
                cmd = ' '.join(cmd.split()[1:])
            if "|" in cmd or ">" in cmd:
                # anything I don't parse, send off
                outside = True
                cmd = "az " + cmd
            telemetry.track_cli_commands_used()

        return break_flag, continue_flag, outside, cmd