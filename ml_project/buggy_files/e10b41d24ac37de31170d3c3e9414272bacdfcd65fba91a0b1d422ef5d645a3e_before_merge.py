def _get_cli():
    @click.group(invoke_without_command=True)
    @global_options
    @click.pass_context
    def cli(ctx, config, verbose):
        # setting the process title so it looks nicer in ps
        # shows up as 'khal' under linux and as 'python: khal (python2.7)'
        # under FreeBSD, which is still nicer than the default
        setproctitle('khal')
        prepare_context(ctx, config, verbose)

        if not ctx.invoked_subcommand:
            command = ctx.obj['conf']['default']['default_command']
            if command:
                ctx.invoke(cli.commands[command])
            else:
                click.echo(ctx.get_help())
                ctx.exit(1)

    @cli.command()
    @time_args
    @multi_calendar_option
    @click.pass_context
    def calendar(ctx, days, events, dates):
        '''Print calendar with agenda.'''
        controllers.calendar(
            build_collection(ctx),
            date=dates,
            firstweekday=ctx.obj['conf']['locale']['firstweekday'],
            encoding=ctx.obj['conf']['locale']['encoding'],
            locale=ctx.obj['conf']['locale'],
            weeknumber=ctx.obj['conf']['locale']['weeknumbers'],
            show_all_days=ctx.obj['conf']['default']['show_all_days'],
            days=days or ctx.obj['conf']['default']['days'],
            events=events
        )

    @cli.command()
    @time_args
    @multi_calendar_option
    @click.pass_context
    def agenda(ctx, days, events, dates):
        '''Print agenda.'''
        controllers.agenda(
            build_collection(ctx),
            date=dates,
            firstweekday=ctx.obj['conf']['locale']['firstweekday'],
            encoding=ctx.obj['conf']['locale']['encoding'],
            show_all_days=ctx.obj['conf']['default']['show_all_days'],
            locale=ctx.obj['conf']['locale'],
            days=days or ctx.obj['conf']['default']['days'],
            events=events,
        )

    @cli.command()
    @calendar_option
    @click.option('--location', '-l',
                  help=('The location of the new event.'))
    @click.option('--repeat', '-r',
                  help=('Repeat event: daily, weekly, monthly or yearly.'))
    @click.option('--until', '-u',
                  help=('Stop an event repeating on this date.'))
    @click.argument('description', nargs=-1, required=True)
    @click.pass_context
    def new(ctx, calendar, description, location, repeat, until):
        '''Create a new event.'''
        controllers.new_from_string(
            build_collection(ctx),
            calendar,
            ctx.obj['conf'],
            list(description),
            location=location,
            repeat=repeat,
            until=until.split(' ') if until is not None else None,
        )

    @cli.command('import')
    @click.option('--include-calendar', '-a', help=('The calendar to use.'),
                  expose_value=False, callback=_calendar_select_callback,
                  metavar='CAL')
    @click.option('--batch', help=('do not ask for any confirmation.'),
                  is_flag=True)
    @click.option('--random_uid', '-r', help=('Select a random uid.'),
                  is_flag=True)
    @click.argument('ics', type=click.File('rb'))
    @click.pass_context
    def import_ics(ctx, ics, batch, random_uid):
        '''Import events from an .ics file.

        If an event with the same UID is already present in the (implicitly)
        selected calendar import will ask before updating (i.e. overwriting)
        that old event with the imported one, unless --batch is given, than it
        will always update. If this behaviour is not desired, use the
        `--random-uid` flag to generate a new, random UID.
        If no calendar is specified (and not `--batch`), you will be asked
        to choose a calendar. You can either enter the number printed behind
        each calendar's name or any unique prefix of a calendar's name.

        '''
        ics_str = ics.read()
        controllers.import_ics(
            build_collection(ctx),
            ctx.obj['conf'],
            ics=ics_str,
            batch=batch,
            random_uid=random_uid
        )

    @cli.command()
    @multi_calendar_option
    @click.pass_context
    def interactive(ctx):
        '''Interactive UI. Also launchable via `ikhal`.'''
        controllers.interactive(build_collection(ctx), ctx.obj['conf'])

    @click.command()
    @multi_calendar_option
    @global_options
    @click.pass_context
    def interactive_cli(ctx, config, verbose):
        '''Interactive UI. Also launchable via `khal interactive`.'''
        prepare_context(ctx, config, verbose)
        controllers.interactive(build_collection(ctx), ctx.obj['conf'])

    @cli.command()
    @multi_calendar_option
    @click.pass_context
    def printcalendars(ctx):
        '''List all calendars.'''
        click.echo('\n'.join(build_collection(ctx).names))

    @cli.command()
    @click.pass_context
    def printformats(ctx):
        '''Print a date in all formats.

        Print the date 2013-12-21 10:09 in all configured date(time)
        formats to check if these locale settings are configured to ones
        liking.'''
        from datetime import datetime
        time = datetime(2013, 12, 21, 10, 9)

        for strftime_format in [
                'longdatetimeformat', 'datetimeformat', 'longdateformat',
                'dateformat', 'timeformat']:
            dt_str = time.strftime(ctx.obj['conf']['locale'][strftime_format])
            click.echo('{}: {}'.format(strftime_format, dt_str))

    @cli.command()
    @multi_calendar_option
    @click.argument('search_string')
    @click.pass_context
    def search(ctx, search_string):
        '''Search for events matching SEARCH_STRING.

        For repetitive events only one event is currently shown.
        '''
        # TODO support for time ranges, location, description etc
        collection = build_collection(ctx)
        events = collection.search(search_string)
        event_column = list()
        term_width, _ = get_terminal_size()
        for event in events:
            desc = textwrap.wrap(event.event_description, term_width)
            event_column.extend([colored(d, event.color) for d in desc])
        click.echo(to_unicode(
            '\n'.join(event_column),
            ctx.obj['conf']['locale']['encoding'])
        )

    @cli.command()
    @multi_calendar_option
    @click.argument('datetime', required=False, nargs=-1)
    @click.pass_context
    def at(ctx, datetime=None):
        '''Show all events scheduled for DATETIME.

        if DATETIME is given (or the string `now`) all events scheduled
        for this moment are shown, if only a time is given, the date is assumed
        to be today
        '''
        collection = build_collection(ctx)
        locale = ctx.obj['conf']['locale']
        dtime_list = list(datetime)
        if dtime_list == [] or dtime_list == ['now']:
            import datetime
            dtime = datetime.datetime.now()
        else:
            try:
                dtime, _ = aux.guessdatetimefstr(dtime_list, locale)
            except ValueError:
                logger.fatal(
                    '{} is not a valid datetime (matches neither {} nor {} nor'
                    ' {})'.format(
                        ' '.join(dtime_list),
                        locale['timeformat'],
                        locale['datetimeformat'],
                        locale['longdatetimeformat']))
                sys.exit(1)
        dtime = locale['local_timezone'].localize(dtime)
        dtime = dtime.astimezone(pytz.UTC)
        events = collection.get_events_at(dtime)
        event_column = list()
        term_width, _ = get_terminal_size()
        for event in events:
            desc = textwrap.wrap(event.event_description, term_width)
            event_column.extend([colored(d, event.color) for d in desc])
        click.echo(to_unicode(
            '\n'.join(event_column),
            ctx.obj['conf']['locale']['encoding'])
        )

    return cli, interactive_cli