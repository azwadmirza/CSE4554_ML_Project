    async def on_ready():
        if bot._uptime is not None:
            return

        bot._uptime = datetime.datetime.utcnow()
        packages = []

        if cli_flags.no_cogs is False:
            packages.extend(await bot._config.packages())

        if cli_flags.load_cogs:
            packages.extend(cli_flags.load_cogs)

        if packages:
            # Load permissions first, for security reasons
            try:
                packages.remove("permissions")
            except ValueError:
                pass
            else:
                packages.insert(0, "permissions")

            to_remove = []
            print("Loading packages...")
            for package in packages:
                try:
                    spec = await bot._cog_mgr.find_cog(package)
                    await bot.load_extension(spec)
                except Exception as e:
                    log.exception("Failed to load package {}".format(package), exc_info=e)
                    await bot.remove_loaded_package(package)
                    to_remove.append(package)
            for package in to_remove:
                packages.remove(package)
            if packages:
                print("Loaded packages: " + ", ".join(packages))

        if bot.rpc_enabled:
            await bot.rpc.initialize()

        guilds = len(bot.guilds)
        users = len(set([m for m in bot.get_all_members()]))

        try:
            data = await bot.application_info()
            invite_url = discord.utils.oauth_url(data.id)
        except:
            invite_url = "Could not fetch invite url"

        prefixes = cli_flags.prefix or (await bot._config.prefix())
        lang = await bot._config.locale()
        red_pkg = pkg_resources.get_distribution("Red-DiscordBot")
        dpy_version = discord.__version__

        INFO = [
            str(bot.user),
            "Prefixes: {}".format(", ".join(prefixes)),
            "Language: {}".format(lang),
            "Red Bot Version: {}".format(red_version),
            "Discord.py Version: {}".format(dpy_version),
            "Shards: {}".format(bot.shard_count),
        ]

        if guilds:
            INFO.extend(("Servers: {}".format(guilds), "Users: {}".format(users)))
        else:
            print("Ready. I'm not in any server yet!")

        INFO.append("{} cogs with {} commands".format(len(bot.cogs), len(bot.commands)))

        with contextlib.suppress(aiohttp.ClientError, discord.HTTPException):
            async with aiohttp.ClientSession() as session:
                async with session.get("https://pypi.python.org/pypi/red-discordbot/json") as r:
                    data = await r.json()
            if VersionInfo.from_str(data["info"]["version"]) > red_version_info:
                INFO.append(
                    "Outdated version! {} is available "
                    "but you're using {}".format(data["info"]["version"], red_version)
                )

                await bot.send_to_owners(
                    "Your Red instance is out of date! {} is the current "
                    "version, however you are using {}!".format(
                        data["info"]["version"], red_version
                    )
                )
        INFO2 = []

        mongo_enabled = storage_type() != "JSON"
        reqs_installed = {"docs": None, "test": None}
        for key in reqs_installed.keys():
            reqs = [x.name for x in red_pkg._dep_map[key]]
            try:
                pkg_resources.require(reqs)
            except DistributionNotFound:
                reqs_installed[key] = False
            else:
                reqs_installed[key] = True

        options = (
            ("MongoDB", mongo_enabled),
            ("Voice", True),
            ("Docs", reqs_installed["docs"]),
            ("Tests", reqs_installed["test"]),
        )

        on_symbol, off_symbol, ascii_border = _get_startup_screen_specs()

        for option, enabled in options:
            enabled = on_symbol if enabled else off_symbol
            INFO2.append("{} {}".format(enabled, option))

        print(Fore.RED + INTRO)
        print(Style.RESET_ALL)
        print(bordered(INFO, INFO2, ascii_border=ascii_border))

        if invite_url:
            print("\nInvite URL: {}\n".format(invite_url))

        bot._color = discord.Colour(await bot._config.color())