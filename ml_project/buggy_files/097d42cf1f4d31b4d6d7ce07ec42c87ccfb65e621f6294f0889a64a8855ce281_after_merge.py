    def start(self, starting: bool = True, error_on_pipeline: bool = True,
              error_on_message: bool = False, source_pipeline: Optional[str] = None,
              destination_pipeline: Optional[str] = None):

        self.__source_pipeline = source_pipeline
        self.__destination_pipeline = destination_pipeline

        while True:
            try:
                if not starting and (error_on_pipeline or error_on_message):
                    self.logger.info('Bot will continue in %s seconds.',
                                     self.parameters.error_retry_delay)
                    time.sleep(self.parameters.error_retry_delay)

                starting = False
                error_on_message = False
                message_to_dump = None

                if error_on_pipeline:
                    try:
                        self.__connect_pipelines()
                    except Exception as exc:
                        raise exceptions.PipelineError(exc)
                    else:
                        error_on_pipeline = False

                self.__handle_sighup()
                self.process()
                self.__error_retries_counter = 0  # reset counter

            except exceptions.PipelineError as exc:
                error_on_pipeline = True

                if self.parameters.error_log_exception:
                    self.logger.exception('Pipeline failed.')
                else:
                    self.logger.error(utils.error_message_from_exc(exc))
                    self.logger.error('Pipeline failed.')
                self.__disconnect_pipelines()

            except exceptions.DecodingError as exc:
                self.logger.exception('Could not decode message from pipeline. No retries useful.')

                # ensure that we do not re-process the faulty message
                self.__error_retries_counter = self.parameters.error_max_retries + 1
                error_on_message = sys.exc_info()

                message_to_dump = exc.object

            except Exception as exc:
                # in case of serious system issues, exit immediately
                if isinstance(exc, MemoryError):
                    self.logger.exception('Out of memory. Exit immediately. Reason: %r.' % exc.args[0])
                    self.stop()
                elif isinstance(exc, (IOError, OSError)) and exc.errno == 28:
                    self.logger.exception('Out of disk space. Exit immediately.')
                    self.stop()

                error_on_message = sys.exc_info()

                if self.parameters.error_log_exception:
                    self.logger.exception("Bot has found a problem.")
                else:
                    self.logger.error(utils.error_message_from_exc(exc))
                    self.logger.error("Bot has found a problem.")

                if self.parameters.error_log_message:
                    # Print full message if explicitly requested by config
                    self.logger.info("Current Message(event): %r.",
                                     self.__current_message)

                # In case of permanent failures, stop now
                if isinstance(exc, exceptions.ConfigurationError):
                    self.stop()

            except KeyboardInterrupt:
                self.logger.info("Received KeyboardInterrupt.")
                self.stop(exitcode=0)

            finally:
                do_rate_limit = False

                if error_on_message or error_on_pipeline:
                    self.__message_counter["failure"] += 1
                    self.__error_retries_counter += 1

                    # reached the maximum number of retries
                    if (self.__error_retries_counter >
                            self.parameters.error_max_retries):

                        if error_on_message:

                            if self.parameters.error_dump_message:
                                error_traceback = traceback.format_exception(*error_on_message)
                                self._dump_message(error_traceback,
                                                   message=message_to_dump if message_to_dump else self.__current_message)
                            else:
                                warnings.warn("Message will be removed from the pipeline and not dumped to the disk. "
                                              "Set `error_dump_message` to true to save the message on disk. "
                                              "This warning is only shown once in the runtime of a bot.")
                            if self.__destination_queues and '_on_error' in self.__destination_queues:
                                self.send_message(self.__current_message, path='_on_error')

                            self.acknowledge_message()

                            # when bot acknowledge the message,
                            # don't need to wait again
                            error_on_message = False

                        # run_mode: scheduled
                        if self.run_mode == 'scheduled':
                            self.logger.info('Shutting down scheduled bot.')
                            self.stop(exitcode=0)

                        # error_procedure: stop
                        elif self.parameters.error_procedure == "stop":
                            self.stop()

                        # error_procedure: pass
                        elif not error_on_pipeline:
                            self.__error_retries_counter = 0  # reset counter
                            do_rate_limit = True
                        # error_procedure: pass and pipeline problem
                        else:
                            # retry forever, see https://github.com/certtools/intelmq/issues/1333
                            # https://lists.cert.at/pipermail/intelmq-users/2018-October/000085.html
                            pass
                else:
                    self.__message_counter["success"] += 1
                    do_rate_limit = True

                    # no errors, check for run mode: scheduled
                    if self.run_mode == 'scheduled':
                        self.logger.info('Shutting down scheduled bot.')
                        self.stop(exitcode=0)

                if getattr(self.parameters, 'testing', False):
                    self.logger.debug('Testing environment detected, returning now.')
                    return

                # Do rate_limit at the end on success and after the retries
                # counter has been reset: https://github.com/certtools/intelmq/issues/1431
                if do_rate_limit:
                    if self.parameters.rate_limit and self.run_mode != 'scheduled':
                        self.__sleep()
                    if self.collector_empty_process and self.run_mode != 'scheduled':
                        self.__sleep(1, log=False)

            self.__stats()
            self.__handle_sighup()