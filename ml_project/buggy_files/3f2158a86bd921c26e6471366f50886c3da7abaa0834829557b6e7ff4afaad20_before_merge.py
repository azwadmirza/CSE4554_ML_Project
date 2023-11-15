    def exit(self, status=0, msg=None):
        # Run the functions on self._mixin_after_parsed_funcs
        for mixin_before_exit_func in self._mixin_before_exit_funcs:  # pylint: disable=no-member
            try:
                mixin_before_exit_func(self)
            except Exception as err:  # pylint: disable=broad-except
                logger = logging.getLogger(__name__)
                logger.exception(err)
                logger.error(
                    'Error while processing {0}: {1}'.format(
                        mixin_before_exit_func, traceback.format_exc(err)
                    )
                )
        if self._setup_mp_logging_listener_ is True:
            # Stop the logging queue listener process
            log.shutdown_multiprocessing_logging_listener(daemonizing=True)
        if isinstance(msg, six.string_types) and msg and msg[-1] != '\n':
            msg = '{0}\n'.format(msg)
        optparse.OptionParser.exit(self, status, msg)