    def _exec_command(command, slot_info, events):
        index = slot_info.rank
        host_name = slot_info.hostname

        host_address = network.resolve_host_address(host_name)
        local_addresses = network.get_local_host_addresses()
        if host_address not in local_addresses:
            command = 'ssh -o PasswordAuthentication=no -o StrictHostKeyChecking=no ' \
                      '{host} {ssh_port_arg} ' \
                      '{local_command}'\
                .format(host=host_name,
                        ssh_port_arg=ssh_port_arg,
                        local_command=quote('cd {pwd} > /dev/null 2>&1 ; {local_command}'
                                            .format(pwd=os.getcwd(), local_command=command)))

        if settings.verbose:
            print(command)

        # Redirect output if requested
        stdout = stderr = None
        stdout_file = stderr_file = None
        if settings.output_filename:
            padded_rank = _pad_rank(index, settings.num_proc)
            output_dir_rank = os.path.join(settings.output_filename, 'rank.{rank}'.format(rank=padded_rank))
            if not os.path.exists(output_dir_rank):
                os.mkdir(output_dir_rank)

            stdout_file = open(os.path.join(output_dir_rank, 'stdout'), 'w')
            stderr_file = open(os.path.join(output_dir_rank, 'stderr'), 'w')

            stdout = MultiFile([sys.stdout, stdout_file])
            stderr = MultiFile([sys.stderr, stderr_file])

        try:
            exit_code = safe_shell_exec.execute(command, index=index, stdout=stdout, stderr=stderr, events=events)
            if exit_code != 0:
                print('Process {idx} exit with status code {ec}.'.format(idx=index, ec=exit_code))
        except Exception as e:
            print('Exception happened during safe_shell_exec, exception '
                  'message: {message}'.format(message=e))
            exit_code = 1
        finally:
            if stdout_file:
                stdout_file.close()
            if stderr_file:
                stderr_file.close()
        return exit_code, time.time()