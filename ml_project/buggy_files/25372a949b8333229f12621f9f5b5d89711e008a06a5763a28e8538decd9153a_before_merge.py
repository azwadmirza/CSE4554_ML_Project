def main():
    parser = argparse.ArgumentParser(
        prog=APPNAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage=USAGE,
        description=DESCRIPTION,
        epilog=EPILOG,
    )

    parser.add_argument('botid', metavar='botid', nargs='?',
                        default=None, help='botid to inspect dumps of')
    args = parser.parse_args()

    # Try to get log_level from defaults_configuration, else use default
    try:
        log_level = utils.load_configuration(DEFAULTS_CONF_FILE)['logging_level']
    except Exception:
        log_level = DEFAULT_LOGGING_LEVEL

    try:
        logger = utils.log('intelmqdump', log_level=log_level)
    except (FileNotFoundError, PermissionError) as exc:
        logger = utils.log('intelmqdump', log_level=log_level, log_path=False)
        logger.error('Not logging to file: %s', exc)

    ctl = intelmqctl.IntelMQController()
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims('')

    pipeline_config = utils.load_configuration(PIPELINE_CONF_FILE)
    pipeline_pipes = {}
    for bot, pipes in pipeline_config.items():
        pipeline_pipes[pipes.get('source-queue', '')] = bot

    if args.botid is None:
        filenames = glob.glob(os.path.join(DEFAULT_LOGGING_PATH, '*.dump'))
        if not len(filenames):
            print(green('Nothing to recover from, no dump files found!'))
            sys.exit(0)
        filenames = [(fname, fname[len(DEFAULT_LOGGING_PATH):-5])
                     for fname in sorted(filenames)]

        length = max([len(value[1]) for value in filenames])
        print(bold("{c:>3}: {s:{length}} {i}".format(c='id', s='name (bot id)',
                                                     i='content',
                                                     length=length)))
        for count, (fname, shortname) in enumerate(filenames):
            info = dump_info(fname)
            print("{c:3}: {s:{length}} {i}".format(c=count, s=shortname, i=info,
                                                   length=length))
        try:
            bot_completer = Completer(possible_values=[f[1] for f in filenames])
            readline.set_completer(bot_completer.complete)
            botid = input(inverted('Which dump file to process (id or name)?') +
                          ' ')
        except EOFError:
            sys.exit(0)
        else:
            botid = botid.strip()
            if botid == 'q' or not botid:
                exit(0)
        try:
            fname, botid = filenames[int(botid)]
        except ValueError:
            fname = os.path.join(DEFAULT_LOGGING_PATH, botid) + '.dump'
    else:
        botid = args.botid
        fname = os.path.join(DEFAULT_LOGGING_PATH, botid) + '.dump'

    if not os.path.isfile(fname):
        print(bold('Given file does not exist: {}'.format(fname)))
        exit(1)

    answer = None
    delete_file = False
    while True:
        with open(fname, 'r+') as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print(red('Dump file is currently locked. Stopping.'))
                break
            info = dump_info(fname, file_descriptor=handle)
            handle.seek(0)
            available_answers = ACTIONS.keys()
            print('Processing {}: {}'.format(bold(botid), info))

            if info.startswith(str(red)):
                available_opts = [item[0] for item in ACTIONS.values() if item[2]]
                available_answers = [k for k, v in ACTIONS.items() if v[2]]
                print('Restricted actions.')
            else:
                # don't display list after 'show', 'recover' & edit commands
                if not (answer and isinstance(answer, list) and answer[0] in ['s', 'r', 'v']):
                    content = json.load(handle)
                    handle.seek(0)
                    content = OrderedDict(sorted(content.items(), key=lambda t: t[0]))  # sort by key here, #1280
                    meta = load_meta(content)

                    available_opts = [item[0] for item in ACTIONS.values()]
                    for count, line in enumerate(meta):
                        print('{:3}: {} {}'.format(count, *line))

            # Determine bot status
            try:
                bot_status = ctl.bot_status(botid)
                if bot_status[1] == 'running':
                    print(red('This bot is currently running, the dump file is now locked and '
                              'the bot can\'t write it.'))
            except KeyError:
                bot_status = 'error'
                print(red('Attention: This bot is not defined!'))
                available_opts = [item[0] for item in ACTIONS.values() if item[2]]
                available_answers = [k for k, v in ACTIONS.items() if v[2]]
                print('Restricted actions.')

            try:
                possible_answers = list(available_answers)
                for id_action in ['r', 'a']:
                    if id_action in possible_answers:
                        possible_answers[possible_answers.index(id_action)] = id_action + ' '
                action_completer = Completer(possible_answers, queues=pipeline_pipes.keys())
                readline.set_completer(action_completer.complete)
                answer = input(inverted(', '.join(available_opts) + '?') + ' ').split()
            except EOFError:
                break
            else:
                if not answer:
                    continue
            if len(answer) == 0 or answer[0] not in available_answers:
                print('Action not allowed.')
                continue
            if any([answer[0] == char for char in AVAILABLE_IDS]) and len(answer) > 1:
                ids = [int(item) for item in answer[1].split(',')]
            else:
                ids = []
            queue_name = None
            if answer[0] == 'a':
                # recover all -> recover all by ids
                answer[0] = 'r'
                ids = range(len(meta))
                if len(answer) > 1:
                    queue_name = answer[1]
            if answer[0] == 'q':
                break
            elif answer[0] == 'e':
                # Delete entries
                for entry in ids:
                    del content[meta[entry][0]]
                save_file(handle, content)
            elif answer[0] == 'r':
                # recover entries
                default = utils.load_configuration(DEFAULTS_CONF_FILE)
                runtime = utils.load_configuration(RUNTIME_CONF_FILE)
                params = utils.load_parameters(default, runtime)
                pipe = pipeline.PipelineFactory.create(params, logger)
                try:
                    for i, (key, entry) in enumerate([item for (count, item)
                                                      in enumerate(content.items()) if count in ids]):
                        if entry['message']:
                            msg = copy.copy(entry['message'])  # otherwise the message field gets converted
                            if isinstance(msg, dict):
                                msg = json.dumps(msg)
                        else:
                            print('No message here, deleting entry.')
                            del content[key]
                            continue

                        if queue_name is None:
                            if len(answer) == 3:
                                queue_name = answer[2]
                            else:
                                queue_name = entry['source_queue']
                        if queue_name in pipeline_pipes:
                            if runtime[pipeline_pipes[queue_name]]['group'] == 'Parser' and json.loads(msg)['__type'] == 'Event':
                                print('Event converted to Report automatically.')
                                msg = message.Report(message.MessageFactory.unserialize(msg)).serialize()
                        try:
                            pipe.set_queues(queue_name, 'destination')
                            pipe.connect()
                            pipe.send(msg)
                        except exceptions.PipelineError:
                            print(red('Could not reinject into queue {}: {}'
                                      ''.format(queue_name, traceback.format_exc())))
                        else:
                            del content[key]
                            print(green('Recovered dump {}.'.format(i)))
                finally:
                    save_file(handle, content)
                if not content:
                    delete_file = True
                    print('Deleting empty file {}'.format(fname))
                    break
            elif answer[0] == 'd':
                # delete dumpfile
                delete_file = True
                print('Deleting empty file {}'.format(fname))
                break
            elif answer[0] == 's':
                # Show entries by id
                for count, (key, orig_value) in enumerate(content.items()):
                    value = copy.copy(orig_value)  # otherwise the raw field gets truncated
                    if count not in ids:
                        continue
                    print('=' * 100, '\nShowing id {} {}\n'.format(count, key),
                          '-' * 50)
                    if isinstance(value['message'], (bytes, str)):
                        value['message'] = json.loads(value['message'])
                        if ('raw' in value['message'] and
                                len(value['message']['raw']) > 1000):
                            value['message']['raw'] = value['message'][
                                'raw'][:1000] + '...[truncated]'
                    if type(value['traceback']) is not list:
                        value['traceback'] = value['traceback'].splitlines()
                    pprint.pprint(value)
            elif answer[0] == 'v':
                # edit given id
                if not ids:
                    print(red('Edit mode needs an id'))
                    continue
                for entry in ids:
                    with tempfile.NamedTemporaryFile(mode='w+t', suffix='.json') as tmphandle:
                        filename = tmphandle.name
                        utils.write_configuration(configuration_filepath=filename,
                                                  content=json.loads(content[meta[entry][0]]['message']),
                                                  new=True,
                                                  backup=False)
                        proc = subprocess.call(['sensible-editor', filename])
                        if proc != 0:
                            print(red('Calling editor failed.'))
                        else:
                            tmphandle.seek(0)
                            content[meta[entry][0]]['message'] = tmphandle.read()
                            save_file(handle, content)

    if delete_file:
        os.remove(fname)