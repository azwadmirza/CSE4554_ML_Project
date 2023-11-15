  def _spawn_pip_isolated(self, args, cache=None, interpreter=None):
    pip_args = ['--disable-pip-version-check', '--isolated', '--exists-action', 'i']

    # The max pip verbosity is -vvv and for pex it's -vvvvvvvvv; so we scale down by a factor of 3.
    pex_verbosity = ENV.PEX_VERBOSE
    pip_verbosity = pex_verbosity // 3
    if pip_verbosity > 0:
      pip_args.append('-{}'.format('v' * pip_verbosity))
    else:
      pip_args.append('-q')

    if cache:
      pip_args.extend(['--cache-dir', cache])
    else:
      pip_args.append('--no-cache-dir')

    command = pip_args + args
    with ENV.strip().patch(PEX_ROOT=ENV.PEX_ROOT, PEX_VERBOSE=str(pex_verbosity)) as env:
      # Guard against API calls from environment with ambient PYTHONPATH preventing pip PEX
      # bootstrapping. See: https://github.com/pantsbuild/pex/issues/892
      pythonpath = env.pop('PYTHONPATH', None)
      if pythonpath:
        TRACER.log('Scrubbed PYTHONPATH={} from the pip PEX environment.'.format(pythonpath), V=3)

      from pex.pex import PEX
      pip = PEX(pex=self._pip_pex_path, interpreter=interpreter)
      return Job(
        command=pip.cmdline(command),
        process=pip.run(
          args=command,
          env=env,
          blocking=False
        )
      )