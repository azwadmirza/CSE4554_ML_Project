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
    ctl = intelmqctl.IntelMQController()

    if args.botid is None:
        filenames = glob.glob(os.path.join(DEFAULT_LOGGING_PATH, '*.dump'))
        if not len(filenames):
            print(green('Nothing to recover from, no dump files found!'))
            exit(0)
        filenames = [(fname, fname[len(DEFAULT_LOGGING_PATH):-5])
                     for fname in sorted(filenames)]

        length = max([len(value[1]) for value in filenames])
        print(bold("{c:>3}: {s:{l}} {i}".format(c='id', s='name (bot id)',
                                                i='content', l=length)))
        for count, (fname, shortname) in enumerate(filenames):
            info = dump_info(fname)
            print("{c:3}: {s:{l}} {i}".format(c=count, s=shortname, i=info,
                                              l=length))
        try:
            botid = input(inverted('Which dump file to process (id or name)?') +
                          ' ')
        except EOFError:
            exit(0)
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
    while True:
        info = dump_info(fname)
        available_answers = ACTIONS.keys()
        print('Processing {}: {}'.format(bold(botid), info))

        if info.startswith(str(red)):
            available_opts = [item[0] for item in ACTIONS.values() if item[2]]
            available_answers = [k for k, v in ACTIONS.items() if v[2]]
            print('Restricted actions.')
        else:
            # don't display list after 'show' and 'recover' command
            if not (answer and isinstance(answer, list) and answer[0] in ['s', 'r']):
                with open(fname, 'rt') as handle:
                    content = json.load(handle)
                meta = load_meta(content)
                available_opts = [item[0] for item in ACTIONS.values()]
                for count, line in enumerate(meta):
                    print('{:3}: {} {}'.format(count, *line))

        # Determine bot status
        try:
            bot_status = ctl.bot_status(botid)
            if bot_status == 'running':
                print(red('Attention: This bot is currently running!'))
        except KeyError:
            bot_status = 'error'
            print(red('Attention: This bot is not defined!'))
            available_opts = [item[0] for item in ACTIONS.values() if item[2]]
            available_answers = [k for k, v in ACTIONS.items() if v[2]]
            print('Restricted actions.')

        try:
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
            save_file(fname, content)
        elif answer[0] == 'r':
            if bot_status == 'running':
                # See https://github.com/certtools/intelmq/issues/574
                print(red('Recovery for running bots not possible.'))
                continue
            # recover entries
            default = utils.load_configuration(DEFAULTS_CONF_FILE)
            runtime = utils.load_configuration(RUNTIME_CONF_FILE)
            params = utils.load_parameters(default, runtime)
            pipe = pipeline.PipelineFactory.create(params)
            try:
                for i, (key, entry) in enumerate([item for (count, item)
                                                  in enumerate(content.items()) if count in ids]):
                    if entry['message']:
                        msg = entry['message']
                    else:
                        print('No message here, deleting entry.')
                        del content[key]
                        continue

                    if queue_name is None:
                        if len(answer) == 3:
                            queue_name = answer[2]
                        else:
                            queue_name = entry['source_queue']
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
                save_file(fname, content)
            if not content:
                os.remove(fname)
                print('Deleted empty file {}'.format(fname))
                break
        elif answer[0] == 'd':
            # delete dumpfile
            os.remove(fname)
            print('Deleted file {}'.format(fname))
            break
        elif answer[0] == 's':
            # Show entries by id
            for count, (key, value) in enumerate(content.items()):
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