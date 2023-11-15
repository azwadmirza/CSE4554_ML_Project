def setup_inject(runner: Runner, args):
    runner.require(["torsocks"], "Please install torsocks (v2.1 or later)")
    if runner.chatty:
        runner.show(
            "Starting proxy with method 'inject-tcp', which has the following "
            "limitations: Go programs, static binaries, suid programs, and "
            "custom DNS implementations are not supported. For a full list of "
            "method limitations see "
            "https://telepresence.io/reference/methods.html"
        )
    command = ["torsocks"] + (args.run or ["bash" "--norc"])

    def launch(runner_, _remote_info, env, socks_port, _ssh, _mount_dir):
        return launch_inject(runner_, command, socks_port, env)

    return launch