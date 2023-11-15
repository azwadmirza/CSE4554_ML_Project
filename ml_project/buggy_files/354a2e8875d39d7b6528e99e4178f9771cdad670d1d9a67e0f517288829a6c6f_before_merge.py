def judge_proc(need_monitor):
    from dmoj import judgeenv

    logfile = judgeenv.log_file

    try:
        logfile = logfile % env['id']
    except TypeError:
        pass

    logging.basicConfig(filename=logfile, level=logging.INFO,
                        format='%(levelname)s %(asctime)s %(process)d %(module)s %(message)s')

    setproctitle('DMOJ Judge: %s on %s' % (env['id'], make_host_port(judgeenv)))

    judge = ClassicJudge(judgeenv.server_host, judgeenv.server_port,
                         secure=judgeenv.secure, no_cert_check=judgeenv.no_cert_check,
                         cert_store=judgeenv.cert_store)
    if need_monitor:
        monitor = Monitor()
        monitor.callback = judge.update_problems
    else:
        monitor = DummyMonitor()

    if hasattr(signal, 'SIGUSR2'):
        def update_problem_signal(signum, frame):
            judge.update_problems()

        signal.signal(signal.SIGUSR2, update_problem_signal)

    if need_monitor and judgeenv.api_listen:
        judge_instance = judge

        class Handler(JudgeControlRequestHandler):
            judge = judge_instance

        api_server = HTTPServer(judgeenv.api_listen, Handler)
        thread = threading.Thread(target=api_server.serve_forever)
        thread.daemon = True
        thread.start()
    else:
        api_server = None

    print()
    with monitor, judge:
        try:
            judge.listen()
        except Exception:
            traceback.print_exc()
        finally:
            judge.murder()
            if api_server:
                api_server.shutdown()