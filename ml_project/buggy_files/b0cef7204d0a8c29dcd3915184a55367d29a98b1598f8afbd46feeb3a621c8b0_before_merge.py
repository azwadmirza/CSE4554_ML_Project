def _run_module(wrapped_cmd, jid, job_path):

    tmp_job_path = job_path + ".tmp"
    jobfile = open(tmp_job_path, "w")
    jobfile.write(json.dumps({"started": 1, "finished": 0, "ansible_job_id": jid}))
    jobfile.close()
    os.rename(tmp_job_path, job_path)
    jobfile = open(tmp_job_path, "w")
    result = {}

    # signal grandchild process started and isolated from being terminated
    # by the connection being closed sending a signal to the job group
    ipc_notifier.send(True)
    ipc_notifier.close()

    outdata = ''
    filtered_outdata = ''
    stderr = ''
    try:
        cmd = shlex.split(wrapped_cmd)
        # call the module interpreter directly (for non-binary modules)
        # this permits use of a script for an interpreter on non-Linux platforms
        interpreter = _get_interpreter(cmd[0])
        if interpreter:
            cmd = interpreter + cmd
        script = subprocess.Popen(cmd, shell=False, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        (outdata, stderr) = script.communicate()
        if PY3:
            outdata = outdata.decode('utf-8', 'surrogateescape')
            stderr = stderr.decode('utf-8', 'surrogateescape')

        (filtered_outdata, json_warnings) = _filter_non_json_lines(outdata)

        result = json.loads(filtered_outdata)

        if json_warnings:
            # merge JSON junk warnings with any existing module warnings
            module_warnings = result.get('warnings', [])
            if not isinstance(module_warnings, list):
                module_warnings = [module_warnings]
            module_warnings.extend(json_warnings)
            result['warnings'] = module_warnings

        if stderr:
            result['stderr'] = stderr
        jobfile.write(json.dumps(result))

    except (OSError, IOError):
        e = sys.exc_info()[1]
        result = {
            "failed": 1,
            "cmd": wrapped_cmd,
            "msg": to_text(e),
            "outdata": outdata,  # temporary notice only
            "stderr": stderr
        }
        result['ansible_job_id'] = jid
        jobfile.write(json.dumps(result))

    except (ValueError, Exception):
        result = {
            "failed": 1,
            "cmd": wrapped_cmd,
            "data": outdata,  # temporary notice only
            "stderr": stderr,
            "msg": traceback.format_exc()
        }
        result['ansible_job_id'] = jid
        jobfile.write(json.dumps(result))

    jobfile.close()
    os.rename(tmp_job_path, job_path)