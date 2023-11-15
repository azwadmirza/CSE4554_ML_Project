    def process(self, argv=None, executable=None, tty=True, cwd=None, env=None, timeout=Timeout.default, run=True,
                stdin=0, stdout=1, stderr=2, preexec_fn=None, preexec_args=(), raw=True, aslr=None, setuid=None,
                shell=False):
        r"""
        Executes a process on the remote server, in the same fashion
        as pwnlib.tubes.process.process.

        To achieve this, a Python script is created to call ``os.execve``
        with the appropriate arguments.

        As an added bonus, the ``ssh_channel`` object returned has a
        ``pid`` property for the process pid.

        Arguments:
            argv(list):
                List of arguments to pass into the process
            executable(str):
                Path to the executable to run.
                If :const:`None`, ``argv[0]`` is used.
            tty(bool):
                Request a `tty` from the server.  This usually fixes buffering problems
                by causing `libc` to write data immediately rather than buffering it.
                However, this disables interpretation of control codes (e.g. Ctrl+C)
                and breaks `.shutdown`.
            cwd(str):
                Working directory.  If :const:`None`, uses the working directory specified
                on :attr:`cwd` or set via :meth:`set_working_directory`.
            env(dict):
                Environment variables to set in the child.  If :const:`None`, inherits the
                default environment.
            timeout(int):
                Timeout to set on the `tube` created to interact with the process.
            run(bool):
                Set to :const:`True` to run the program (default).
                If :const:`False`, returns the path to an executable Python script on the
                remote server which, when executed, will do it.
            stdin(int, str):
                If an integer, replace stdin with the numbered file descriptor.
                If a string, a open a file with the specified path and replace
                stdin with its file descriptor.  May also be one of ``sys.stdin``,
                ``sys.stdout``, ``sys.stderr``.  If :const:`None`, the file descriptor is closed.
            stdout(int, str):
                See ``stdin``.
            stderr(int, str):
                See ``stdin``.
            preexec_fn(callable):
                Function which is executed on the remote side before execve().
                This **MUST** be a self-contained function -- it must perform
                all of its own imports, and cannot refer to variables outside
                its scope.
            preexec_args(object):
                Argument passed to ``preexec_fn``.
                This **MUST** only consist of native Python objects.
            raw(bool):
                If :const:`True`, disable TTY control code interpretation.
            aslr(bool):
                See :class:`pwnlib.tubes.process.process` for more information.
            setuid(bool):
                See :class:`pwnlib.tubes.process.process` for more information.
            shell(bool):
                Pass the command-line arguments to the shell.

        Returns:
            A new SSH channel, or a path to a script if ``run=False``.

        Notes:
            Requires Python on the remote server.

        Examples:
            >>> s = ssh(host='example.pwnme',
            ...         user='runner',
            ...         password='demopass')
            >>> sh = s.process('/bin/sh', env={'PS1':''})
            >>> sh.sendline(b'echo Hello; exit')
            >>> sh.recvall()
            b'Hello\n'
            >>> s.process(['/bin/echo', b'\xff']).recvall()
            b'\xff\n'
            >>> s.process(['readlink', '/proc/self/exe']).recvall()
            b'/bin/readlink\n'
            >>> s.process(['LOLOLOL', '/proc/self/exe'], executable='readlink').recvall()
            b'/bin/readlink\n'
            >>> s.process(['LOLOLOL\x00', '/proc/self/cmdline'], executable='cat').recvall()
            b'LOLOLOL\x00/proc/self/cmdline\x00'
            >>> sh = s.process(executable='/bin/sh')
            >>> str(sh.pid).encode() in s.pidof('sh') # doctest: +SKIP
            True
            >>> s.process(['pwd'], cwd='/tmp').recvall()
            b'/tmp\n'
            >>> p = s.process(['python','-c','import os; os.write(1, os.read(2, 1024))'], stderr=0)
            >>> p.send(b'hello')
            >>> p.recv()
            b'hello'
            >>> s.process(['/bin/echo', 'hello']).recvall()
            b'hello\n'
            >>> s.process(['/bin/echo', 'hello'], stdout='/dev/null').recvall()
            b''
            >>> s.process(['/usr/bin/env'], env={}).recvall()
            b''
            >>> s.process('/usr/bin/env', env={'A':'B'}).recvall()
            b'A=B\n'

            >>> s.process('false', preexec_fn=1234)
            Traceback (most recent call last):
            ...
            PwnlibException: preexec_fn must be a function

            >>> s.process('false', preexec_fn=lambda: 1234)
            Traceback (most recent call last):
            ...
            PwnlibException: preexec_fn cannot be a lambda

            >>> def uses_globals():
            ...     foo = bar
            >>> print(s.process('false', preexec_fn=uses_globals).recvall().strip().decode()) # doctest: +ELLIPSIS
            Traceback (most recent call last):
            ...
            NameError: name 'bar' is not defined

            >>> s.process('echo hello', shell=True).recvall()
            b'hello\n'
        """
        if not argv and not executable:
            self.error("Must specify argv or executable")

        argv      = argv or []
        aslr      = aslr if aslr is not None else context.aslr

        if isinstance(argv, (six.text_type, six.binary_type)):
            argv = [argv]

        if not isinstance(argv, (list, tuple)):
            self.error('argv must be a list or tuple')

        if not all(isinstance(arg, (six.text_type, six.binary_type)) for arg in argv):
            self.error("argv must be strings or bytes: %r" % argv)

        if shell:
            if len(argv) != 1:
                self.error('Cannot provide more than 1 argument if shell=True')
            argv = ['/bin/sh', '-c'] + argv

        # Create a duplicate so we can modify it
        argv = list(argv or [])

        # Python doesn't like when an arg in argv contains '\x00'
        # -> execve() arg 2 must contain only strings
        for i, oarg in enumerate(argv):
            if isinstance(oarg, six.text_type):
                arg = oarg.encode('utf-8')
            else:
                arg = oarg
            if b'\x00' in arg[:-1]:
                self.error('Inappropriate nulls in argv[%i]: %r' % (i, oarg))
            argv[i] = bytearray(arg.rstrip(b'\x00'))

        if env is not None and not isinstance(env, dict) and env != os.environ:
            self.error("env must be a dict: %r" % env)

        # Converts the environment variables to a list of tuples to retain order.
        env2 = []
        # Python also doesn't like when envp contains '\x00'
        if env and hasattr(env, 'items'):
            for k, v in env.items():
                if isinstance(k, six.text_type):
                    k = k.encode('utf-8')
                if isinstance(v, six.text_type):
                    v = v.encode('utf-8')
                if b'\x00' in k[:-1]:
                    self.error('Inappropriate nulls in environment key %r' % k)
                if b'\x00' in v[:-1]:
                    self.error('Inappropriate nulls in environment value %r=%r' % (k, v))
                env2.append((bytearray(k.rstrip(b'\x00')), bytearray(v.rstrip(b'\x00'))))
        env = env2 or env

        executable = executable or argv[0]
        cwd        = cwd or self.cwd

        # Validate, since failures on the remote side will suck.
        if not isinstance(executable, (six.text_type, six.binary_type, bytearray)):
            self.error("executable / argv[0] must be a string: %r" % executable)
        executable = context._decode(executable)

        # Allow passing in sys.stdin/stdout/stderr objects
        handles = {sys.stdin: 0, sys.stdout:1, sys.stderr:2}
        stdin  = handles.get(stdin, stdin)
        stdout = handles.get(stdout, stdout)
        stderr = handles.get(stderr, stderr)

        # Allow the user to provide a self-contained function to run
        def func(): pass
        func      = preexec_fn or func
        func_args = preexec_args

        if not isinstance(func, types.FunctionType):
            self.error("preexec_fn must be a function")

        func_name = func.__name__
        if func_name == (lambda: 0).__name__:
            self.error("preexec_fn cannot be a lambda")

        func_src  = inspect.getsource(func).strip()
        setuid = True if setuid is None else bool(setuid)
        
        script = r"""
#!/usr/bin/env python
import os, sys, ctypes, resource, platform, stat
from collections import OrderedDict
exe   = %(executable)r
argv  = [bytes(a) for a in %(argv)r]
env   = %(env)r

os.chdir(%(cwd)r)

if env is not None:
    env = OrderedDict((bytes(k), bytes(v)) for k,v in env)
    os.environ.clear()
    getattr(os, 'environb', os.environ).update(env)
else:
    env = os.environ

def is_exe(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)

PATH = os.environ.get('PATH','').split(os.pathsep)

if os.path.sep not in exe and not is_exe(exe):
    for path in PATH:
        test_path = os.path.join(path, exe)
        if is_exe(test_path):
            exe = test_path
            break

if not is_exe(exe):
    sys.stderr.write('3\n')
    sys.stderr.write("{} is not executable or does not exist in $PATH: {}".format(exe,PATH))
    sys.exit(-1)

if not %(setuid)r:
    PR_SET_NO_NEW_PRIVS = 38
    result = ctypes.CDLL('libc.so.6').prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)

    if result != 0:
        sys.stdout.write('3\n')
        sys.stdout.write("Could not disable setuid: prctl(PR_SET_NO_NEW_PRIVS) failed")
        sys.exit(-1)

try:
    PR_SET_PTRACER = 0x59616d61
    PR_SET_PTRACER_ANY = -1
    ctypes.CDLL('libc.so.6').prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0)
except Exception:
    pass

# Determine what UID the process will execute as
# This is used for locating apport core dumps
suid = os.getuid()
sgid = os.getgid()
st = os.stat(exe)
if %(setuid)r:
    if (st.st_mode & stat.S_ISUID):
        suid = st.st_uid
    if (st.st_mode & stat.S_ISGID):
        sgid = st.st_gid

if sys.argv[-1] == 'check':
    sys.stdout.write("1\n")
    sys.stdout.write(str(os.getpid()) + "\n")
    sys.stdout.write(str(os.getuid()) + "\n")
    sys.stdout.write(str(os.getgid()) + "\n")
    sys.stdout.write(str(suid) + "\n")
    sys.stdout.write(str(sgid) + "\n")
    sys.stdout.write(os.path.realpath(exe) + '\x00')
    sys.stdout.flush()

for fd, newfd in {0: %(stdin)r, 1: %(stdout)r, 2:%(stderr)r}.items():
    if newfd is None:
        os.close(fd)
    elif isinstance(newfd, (str, bytes)):
        newfd = os.open(newfd, os.O_RDONLY if fd == 0 else (os.O_RDWR|os.O_CREAT))
        os.dup2(newfd, fd)
        os.close(newfd)
    elif isinstance(newfd, int) and newfd != fd:
        os.dup2(fd, newfd)

if not %(aslr)r:
    if platform.system().lower() == 'linux' and %(setuid)r is not True:
        ADDR_NO_RANDOMIZE = 0x0040000
        ctypes.CDLL('libc.so.6').personality(ADDR_NO_RANDOMIZE)

    resource.setrlimit(resource.RLIMIT_STACK, (-1, -1))

# Attempt to dump ALL core file regions
try:
    with open('/proc/self/coredump_filter', 'w') as core_filter:
        core_filter.write('0x3f\n')
except Exception:
    pass

# Assume that the user would prefer to have core dumps.
try:
    resource.setrlimit(resource.RLIMIT_CORE, (-1, -1))
except Exception:
    pass

%(func_src)s
%(func_name)s(*%(func_args)r)

os.execve(exe, argv, env)
""" % locals()

        script = script.strip()

        self.debug("Created execve script:\n" + script)

        if not run:
            with context.local(log_level='error'):
                tmpfile = self.mktemp('-t', 'pwnlib-execve-XXXXXXXXXX')
                self.chmod('+x', tmpfile)

            self.info("Uploading execve script to %r" % tmpfile)
            self.upload_data(script, tmpfile)
            return tmpfile

        if self.isEnabledFor(logging.DEBUG):
            execve_repr = "execve(%r, %s, %s)" % (executable,
                                                  argv,
                                                  'os.environ'
                                                  if (env in (None, os.environ))
                                                  else env)
            # Avoid spamming the screen
            if self.isEnabledFor(logging.DEBUG) and len(execve_repr) > 512:
                execve_repr = execve_repr[:512] + '...'
        else:
            execve_repr = repr(executable)

        msg = 'Starting remote process %s on %s' % (execve_repr, self.host)

        with self.progress(msg) as h:

            script = 'for py in python3 python; do test -x "$(which $py 2>&1)" && exec $py -c %s check; done; echo 2' % sh_string(script)
            with context.local(log_level='error'):
                python = ssh_process(self, script, tty=True, raw=True, level=self.level, timeout=self.timeout)

            try:
                result = safeeval.const(python.recvline())
            except (EOFError, ValueError):
                h.failure("Process creation failed")
                self.warn_once('Could not find a Python interpreter on %s\n' % self.host \
                               + "Use ssh.run() instead of ssh.process()")
                return None

            # If an error occurred, try to grab as much output
            # as we can.
            if result != 1:
                error_message = python.recvrepeat(timeout=1)

            if result == 0:
                self.error("%r does not exist or is not executable" % executable)
            elif result == 3:
                self.error(error_message)
            elif result == 2:
                self.error("python is not installed on the remote system %r" % self.host)
            elif result != 1:
                h.failure("something bad happened:\n%s" % error_message)

            python.pid  = safeeval.const(python.recvline())
            python.uid  = safeeval.const(python.recvline())
            python.gid  = safeeval.const(python.recvline())
            python.suid = safeeval.const(python.recvline())
            python.sgid = safeeval.const(python.recvline())
            python.argv = argv
            python.executable = python.recvuntil(b'\x00')[:-1]

            h.success('pid %i' % python.pid)

        if aslr == False and setuid and (python.uid != python.suid or python.gid != python.sgid):
            effect = "partial" if self.aslr_ulimit else "no"
            message = "Specfied aslr=False on setuid binary %s\n" % python.executable
            message += "This will have %s effect.  Add setuid=False to disable ASLR for debugging.\n" % effect

            if self.aslr_ulimit:
                message += "Unlimited stack size should de-randomize shared libraries."

            self.warn_once(message)

        elif not aslr:
            self.warn_once("ASLR is disabled for %r!" % python.executable)

        return python