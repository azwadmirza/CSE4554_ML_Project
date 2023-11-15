def main():
  start_time = time.time()

  exiter = Exiter()
  ExceptionSink.reset_exiter(exiter)

  with maybe_profiled(os.environ.get('PANTSC_PROFILE')):
    try:
      PantsRunner(exiter, start_time=start_time).run()
    except KeyboardInterrupt as e:
      exiter.exit_and_fail('Interrupted by user:\n{}'.format(e))