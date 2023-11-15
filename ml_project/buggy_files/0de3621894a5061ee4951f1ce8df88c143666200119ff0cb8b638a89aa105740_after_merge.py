    def prompt(self, message='', **kwargs):
        """Get input from the user and return it.

        This is a wrapper around a lot of prompt_toolkit functionality and
        can be a replacement for raw_input. (or GNU readline.) If you want
        to keep your history across several calls, create one
        `~prompt_toolkit.history.History instance and pass it every
        time. This function accepts many keyword arguments. Except for the
        following. they are a proxy to the arguments of
        create_prompt_application().

        Parameters
        ----------
        patch_stdout : file-like, optional
            Replace ``sys.stdout`` by a proxy that ensures that print
            statements from other threads won't destroy the prompt. (They
            will be printed above the prompt instead.)
        return_asyncio_coroutine : bool, optional
            When True, return a asyncio coroutine. (Python >3.3)

        Notes
        -----
        This method was forked from the mainline prompt-toolkit repo.
        Copyright (c) 2014, Jonathan Slenders, All rights reserved.
        """
        patch_stdout = kwargs.pop('patch_stdout', False)
        return_asyncio_coroutine = kwargs.pop('return_asyncio_coroutine', False)
        if return_asyncio_coroutine:
            eventloop = create_asyncio_eventloop()
        else:
            eventloop = kwargs.pop('eventloop', None) or create_eventloop()

        # Create CommandLineInterface.
        if self.cli is None:
            if self.major_minor < (0, 57):
                kwargs.pop('reserve_space_for_menu', None)
            if self.major_minor <= (0, 57):
                kwargs.pop('get_rprompt_tokens', None)
                kwargs.pop('get_continuation_tokens', None)
            cli = CommandLineInterface(
                application=create_prompt_application(message, **kwargs),
                eventloop=eventloop,
                output=create_output())
            self.cli = cli
        else:
            cli = self.cli

        # Replace stdout.
        patch_context = cli.patch_stdout_context() if patch_stdout else DummyContext()

        # Read input and return it.
        if return_asyncio_coroutine:
            # Create an asyncio coroutine and call it.
            exec_context = {'patch_context': patch_context, 'cli': cli}
            exec_(textwrap.dedent('''
            import asyncio
            @asyncio.coroutine
            def prompt_coro():
                with patch_context:
                    document = yield from cli.run_async(reset_current_buffer=False)
                    if document:
                        return document.text
            '''), exec_context)
            return exec_context['prompt_coro']()
        else:
            # Note: We pass `reset_current_buffer=False`, because that way
            # it's easy to give DEFAULT_BUFFER a default value, without it
            # getting erased. We don't have to reset anyway, because this is
            # the first and only time that this CommandLineInterface will run.
            try:
                with patch_context:
                    document = cli.run(reset_current_buffer=False)

                    if document:
                        return document.text
            finally:
                eventloop.close()