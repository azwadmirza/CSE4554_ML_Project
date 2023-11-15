    def run_cli(self):
        iterations = 0
        sqlexecute = self.sqlexecute
        logger = self.logger
        self.configure_pager()

        if self.smart_completion:
            self.refresh_completions()

        author_file = os.path.join(PACKAGE_ROOT, 'AUTHORS')
        sponsor_file = os.path.join(PACKAGE_ROOT, 'SPONSORS')

        key_binding_manager = mycli_bindings()

        if not self.less_chatty:
            print('Version:', __version__)
            print('Chat: https://gitter.im/dbcli/mycli')
            print('Mail: https://groups.google.com/forum/#!forum/mycli-users')
            print('Home: http://mycli.net')
            print('Thanks to the contributor -', thanks_picker([author_file, sponsor_file]))

        def prompt_tokens(cli):
            prompt = self.get_prompt(self.prompt_format)
            if self.prompt_format == self.default_prompt and len(prompt) > self.max_len_prompt:
                prompt = self.get_prompt('\\d> ')
            return [(Token.Prompt, prompt)]

        def get_continuation_tokens(cli, width):
            continuation_prompt = self.get_prompt(self.prompt_continuation_format)
            return [(Token.Continuation, ' ' * (width - len(continuation_prompt)) + continuation_prompt)]

        def show_suggestion_tip():
            return iterations < 2

        def one_iteration(document=None):
            if document is None:
                document = self.cli.run()

                special.set_expanded_output(False)

                try:
                    document = self.handle_editor_command(self.cli, document)
                except RuntimeError as e:
                    logger.error("sql: %r, error: %r", document.text, e)
                    logger.error("traceback: %r", traceback.format_exc())
                    self.echo(str(e), err=True, fg='red')
                    return

            if not document.text.strip():
                return

            if self.destructive_warning:
                destroy = confirm_destructive_query(document.text)
                if destroy is None:
                    pass  # Query was not destructive. Nothing to do here.
                elif destroy is True:
                    self.echo('Your call!')
                else:
                    self.echo('Wise choice!')
                    return

            # Keep track of whether or not the query is mutating. In case
            # of a multi-statement query, the overall query is considered
            # mutating if any one of the component statements is mutating
            mutating = False

            try:
                logger.debug('sql: %r', document.text)

                special.write_tee(self.get_prompt(self.prompt_format) + document.text)
                if self.logfile:
                    self.logfile.write('\n# %s\n' % datetime.now())
                    self.logfile.write(document.text)
                    self.logfile.write('\n')

                successful = False
                start = time()
                res = sqlexecute.run(document.text)
                self.formatter.query = document.text
                successful = True
                result_count = 0
                for title, cur, headers, status in res:
                    logger.debug("headers: %r", headers)
                    logger.debug("rows: %r", cur)
                    logger.debug("status: %r", status)
                    threshold = 1000
                    if (is_select(status) and
                            cur and cur.rowcount > threshold):
                        self.echo('The result set has more than {} rows.'.format(
                            threshold), fg='red')
                        if not click.confirm('Do you want to continue?'):
                            self.echo("Aborted!", err=True, fg='red')
                            break

                    if self.auto_vertical_output:
                        max_width = self.cli.output.get_size().columns
                    else:
                        max_width = None

                    formatted = self.format_output(
                        title, cur, headers, special.is_expanded_output(),
                        max_width)

                    t = time() - start
                    try:
                        if result_count > 0:
                            self.echo('')
                        try:
                            self.output(formatted, status)
                        except KeyboardInterrupt:
                            pass
                        if special.is_timing_enabled():
                            self.echo('Time: %0.03fs' % t)
                    except KeyboardInterrupt:
                        pass

                    start = time()
                    result_count += 1
                    mutating = mutating or is_mutating(status)
                special.unset_once_if_written()
            except EOFError as e:
                raise e
            except KeyboardInterrupt:
                # get last connection id
                connection_id_to_kill = sqlexecute.connection_id
                logger.debug("connection id to kill: %r", connection_id_to_kill)
                # Restart connection to the database
                sqlexecute.connect()
                try:
                    for title, cur, headers, status in sqlexecute.run('kill %s' % connection_id_to_kill):
                        status_str = str(status).lower()
                        if status_str.find('ok') > -1:
                            logger.debug("cancelled query, connection id: %r, sql: %r",
                                         connection_id_to_kill, document.text)
                            self.echo("cancelled query", err=True, fg='red')
                except Exception as e:
                    self.echo('Encountered error while cancelling query: {}'.format(e),
                              err=True, fg='red')
            except NotImplementedError:
                self.echo('Not Yet Implemented.', fg="yellow")
            except OperationalError as e:
                logger.debug("Exception: %r", e)
                if (e.args[0] in (2003, 2006, 2013)):
                    logger.debug('Attempting to reconnect.')
                    self.echo('Reconnecting...', fg='yellow')
                    try:
                        sqlexecute.connect()
                        logger.debug('Reconnected successfully.')
                        one_iteration(document)
                        return  # OK to just return, cuz the recursion call runs to the end.
                    except OperationalError as e:
                        logger.debug('Reconnect failed. e: %r', e)
                        self.echo(str(e), err=True, fg='red')
                        # If reconnection failed, don't proceed further.
                        return
                else:
                    logger.error("sql: %r, error: %r", document.text, e)
                    logger.error("traceback: %r", traceback.format_exc())
                    self.echo(str(e), err=True, fg='red')
            except Exception as e:
                logger.error("sql: %r, error: %r", document.text, e)
                logger.error("traceback: %r", traceback.format_exc())
                self.echo(str(e), err=True, fg='red')
            else:
                if is_dropping_database(document.text, self.sqlexecute.dbname):
                    self.sqlexecute.dbname = None
                    self.sqlexecute.connect()

                # Refresh the table names and column names if necessary.
                if need_completion_refresh(document.text):
                    self.refresh_completions(
                            reset=need_completion_reset(document.text))
            finally:
                if self.logfile is False:
                    self.echo("Warning: This query was not logged.",
                              err=True, fg='red')
            query = Query(document.text, successful, mutating)
            self.query_history.append(query)

        get_toolbar_tokens = create_toolbar_tokens_func(
            self.completion_refresher.is_refreshing,
            show_suggestion_tip)

        layout = create_prompt_layout(
            lexer=MyCliLexer,
            multiline=True,
            get_prompt_tokens=prompt_tokens,
            get_continuation_tokens=get_continuation_tokens,
            get_bottom_toolbar_tokens=get_toolbar_tokens,
            display_completions_in_columns=self.wider_completion_menu,
            extra_input_processors=[ConditionalProcessor(
                processor=HighlightMatchingBracketProcessor(chars='[](){}'),
                filter=HasFocus(DEFAULT_BUFFER) & ~IsDone()
            )],
            reserve_space_for_menu=self.get_reserved_space()
        )
        with self._completer_lock:
            buf = CLIBuffer(always_multiline=self.multi_line, completer=self.completer,
                            history=FileHistory(os.path.expanduser(
                                os.environ.get('MYCLI_HISTFILE', '~/.mycli-history'))),
                            auto_suggest=AutoSuggestFromHistory(),
                            complete_while_typing=Always(), accept_action=AcceptAction.RETURN_DOCUMENT)

            if self.key_bindings == 'vi':
                editing_mode = EditingMode.VI
            else:
                editing_mode = EditingMode.EMACS

            application = Application(
                style=style_from_pygments(style_cls=self.output_style),
                layout=layout, buffer=buf,
                key_bindings_registry=key_binding_manager.registry,
                on_exit=AbortAction.RAISE_EXCEPTION,
                on_abort=AbortAction.RETRY, editing_mode=editing_mode,
                ignore_case=True)
            self.cli = CommandLineInterface(application=application,
                                       eventloop=create_eventloop())

        try:
            while True:
                one_iteration()
                iterations += 1
        except EOFError:
            special.close_tee()
            if not self.less_chatty:
                self.echo('Goodbye!')