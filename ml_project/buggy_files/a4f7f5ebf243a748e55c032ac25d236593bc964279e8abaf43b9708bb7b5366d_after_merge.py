        def run_in_thread(tox_env, os_env, processes):
            output = None
            env_name = tox_env.envconfig.envname
            status = "skipped tests" if config.option.notest else None
            try:
                os_env[str(PARALLEL_ENV_VAR_KEY_PRIVATE)] = str(env_name)
                os_env[str(PARALLEL_ENV_VAR_KEY_PUBLIC)] = str(env_name)
                args_sub = list(args)
                if hasattr(tox_env, "package"):
                    args_sub.insert(position, str(tox_env.package))
                    args_sub.insert(position, "--installpkg")
                if tox_env.get_result_json_path():
                    result_json_index = args_sub.index("--result-json")
                    args_sub[result_json_index + 1] = "{}".format(tox_env.get_result_json_path())
                with tox_env.new_action("parallel {}".format(tox_env.name)) as action:

                    def collect_process(process):
                        processes[tox_env] = (action, process)

                    print_out = not live_out and tox_env.envconfig.parallel_show_output
                    output = action.popen(
                        args=args_sub,
                        env=os_env,
                        redirect=not live_out,
                        capture_err=print_out,
                        callback=collect_process,
                        returnout=print_out,
                    )

            except InvocationError as err:
                status = "parallel child exit code {}".format(err.exit_code)
            finally:
                semaphore.release()
                finished.set()
                tox_env.status = status
                done.add(env_name)
                outcome = spinner.succeed
                if config.option.notest:
                    outcome = spinner.skip
                elif status is not None:
                    outcome = spinner.fail
                outcome(env_name)
                if print_out and output is not None:
                    reporter.verbosity0(output)