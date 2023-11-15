def f_reload(bot, trigger):
    """Reloads a module, for use by admins only."""
    if not trigger.admin:
        return

    name = trigger.group(2)
    if name == bot.config.core.owner:
        return bot.reply('What?')

    if not name or name == '*' or name.upper() == 'ALL THE THINGS':
        bot._callables = {
            'high': collections.defaultdict(list),
            'medium': collections.defaultdict(list),
            'low': collections.defaultdict(list)
        }
        bot.command_groups = collections.defaultdict(list)
        bot.setup()
        return bot.reply('done')

    if name not in sys.modules:
        return bot.reply('%s: not loaded, try the `load` command' % name)

    old_module = sys.modules[name]

    old_callables = {}
    for obj_name, obj in iteritems(vars(old_module)):
        bot.unregister(obj)

    # Also remove all references to sopel callables from top level of the
    # module, so that they will not get loaded again if reloading the
    # module does not override them.
    for obj_name in old_callables.keys():
        delattr(old_module, obj_name)

    # Also delete the setup function
    if hasattr(old_module, "setup"):
        delattr(old_module, "setup")

    modules = sopel.loader.enumerate_modules(bot.config)
    path, type_ = modules[name]
    load_module(bot, name, path, type_)