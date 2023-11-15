    def main(self, args):
        options, args = self.parse_args(args)

        level = 1  # Notify
        level += options.verbose
        level -= options.quiet
        level = logger.level_for_integer(4 - level)
        complete_log = []
        logger.add_consumers(
            (level, sys.stdout),
            (logger.DEBUG, complete_log.append),
        )
        if options.log_explicit_levels:
            logger.explicit_levels = True

        self.setup_logging()

        #TODO: try to get these passing down from the command?
        #      without resorting to os.environ to hold these.

        if options.no_input:
            os.environ['PIP_NO_INPUT'] = '1'

        if options.exists_action:
            os.environ['PIP_EXISTS_ACTION'] = ' '.join(options.exists_action)

        if options.cert:
            os.environ['PIP_CERT'] = options.cert

        if options.require_venv:
            # If a venv is required check if it can really be found
            if not os.environ.get('VIRTUAL_ENV'):
                logger.fatal('Could not find an activated virtualenv (required).')
                sys.exit(VIRTUALENV_NOT_FOUND)

        if options.log:
            log_fp = open_logfile(options.log, 'a')
            logger.add_consumers((logger.DEBUG, log_fp))
        else:
            log_fp = None

        socket.setdefaulttimeout(options.timeout or None)

        urlopen.setup(proxystr=options.proxy, prompting=not options.no_input)

        exit = SUCCESS
        store_log = False
        try:
            status = self.run(options, args)
            # FIXME: all commands should return an exit status
            # and when it is done, isinstance is not needed anymore
            if isinstance(status, int):
                exit = status
        except PreviousBuildDirError:
            e = sys.exc_info()[1]
            logger.fatal(str(e))
            logger.info('Exception information:\n%s' % format_exc())
            store_log = True
            exit = PREVIOUS_BUILD_DIR_ERROR
        except (InstallationError, UninstallationError):
            e = sys.exc_info()[1]
            logger.fatal(str(e))
            logger.info('Exception information:\n%s' % format_exc())
            store_log = True
            exit = ERROR
        except BadCommand:
            e = sys.exc_info()[1]
            logger.fatal(str(e))
            logger.info('Exception information:\n%s' % format_exc())
            store_log = True
            exit = ERROR
        except CommandError:
            e = sys.exc_info()[1]
            logger.fatal('ERROR: %s' % e)
            logger.info('Exception information:\n%s' % format_exc())
            exit = ERROR
        except KeyboardInterrupt:
            logger.fatal('Operation cancelled by user')
            logger.info('Exception information:\n%s' % format_exc())
            store_log = True
            exit = ERROR
        except:
            logger.fatal('Exception:\n%s' % format_exc())
            store_log = True
            exit = UNKNOWN_ERROR
        if store_log:
            log_file_fn = options.log_file
            text = '\n'.join(complete_log)
            try:
                log_file_fp = open_logfile(log_file_fn, 'w')
            except IOError:
                temp = tempfile.NamedTemporaryFile(delete=False)
                log_file_fn = temp.name
                log_file_fp = open_logfile(log_file_fn, 'w')
            logger.fatal('Storing complete log in %s' % log_file_fn)
            log_file_fp.write(text)
            log_file_fp.close()
        if log_fp is not None:
            log_fp.close()
        return exit