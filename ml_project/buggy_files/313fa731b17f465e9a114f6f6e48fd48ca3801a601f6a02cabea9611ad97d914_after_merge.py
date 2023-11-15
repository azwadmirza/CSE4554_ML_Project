    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> Tuple[Optional[str], discord.User, Optional[discord.Guild], bool]:

        target_scope: Optional[str] = None
        target_user: Optional[Union[discord.Member, discord.User]] = None
        target_guild: Optional[discord.Guild] = None
        specified_user = False

        argument = argument.replace("—", "--")

        command, *arguments = argument.split(" -- ")
        if arguments:
            argument = " -- ".join(arguments)
        else:
            command = ""

        parser = NoExitParser(description="Playlist Scope Parsing.", add_help=False)
        parser.add_argument("--scope", nargs="*", dest="scope", default=[])
        parser.add_argument("--guild", nargs="*", dest="guild", default=[])
        parser.add_argument("--server", nargs="*", dest="guild", default=[])
        parser.add_argument("--author", nargs="*", dest="author", default=[])
        parser.add_argument("--user", nargs="*", dest="author", default=[])
        parser.add_argument("--member", nargs="*", dest="author", default=[])

        if not command:
            parser.add_argument("command", nargs="*")

        try:
            vals = vars(parser.parse_args(argument.split()))
        except Exception as exc:
            raise commands.BadArgument() from exc

        if vals["scope"]:
            scope_raw = " ".join(vals["scope"]).strip()
            scope = scope_raw.upper().strip()
            valid_scopes = PlaylistScope.list() + [
                "GLOBAL",
                "GUILD",
                "AUTHOR",
                "USER",
                "SERVER",
                "MEMBER",
                "BOT",
            ]
            if scope not in valid_scopes:
                raise commands.ArgParserFailure("--scope", scope_raw, custom_help=_(_SCOPE_HELP))
            target_scope = standardize_scope(scope)
        elif "--scope" in argument and not vals["scope"]:
            raise commands.ArgParserFailure("--scope", _("Nothing"), custom_help=_(_SCOPE_HELP))

        is_owner = await ctx.bot.is_owner(ctx.author)
        guild = vals.get("guild", None) or vals.get("server", None)
        if is_owner and guild:
            server_error = ""
            target_guild = None
            guild_raw = " ".join(guild).strip()
            try:
                target_guild = await global_unique_guild_finder(ctx, guild_raw)
            except TooManyMatches as err:
                server_error = f"{err}\n"
            except NoMatchesFound as err:
                server_error = f"{err}\n"
            if target_guild is None:
                raise commands.ArgParserFailure(
                    "--guild", guild_raw, custom_help=f"{server_error}{_(_GUILD_HELP)}"
                )

        elif not is_owner and (guild or any(x in argument for x in ["--guild", "--server"])):
            raise commands.BadArgument(_("You cannot use `--guild`"))
        elif any(x in argument for x in ["--guild", "--server"]):
            raise commands.ArgParserFailure("--guild", _("Nothing"), custom_help=_(_GUILD_HELP))

        author = vals.get("author", None) or vals.get("user", None) or vals.get("member", None)
        if author:
            user_error = ""
            target_user = None
            user_raw = " ".join(author).strip()
            try:
                target_user = await global_unique_user_finder(ctx, user_raw, guild=target_guild)
                specified_user = True
            except TooManyMatches as err:
                user_error = f"{err}\n"
            except NoMatchesFound as err:
                user_error = f"{err}\n"

            if target_user is None:
                raise commands.ArgParserFailure(
                    "--author", user_raw, custom_help=f"{user_error}{_(_USER_HELP)}"
                )
        elif any(x in argument for x in ["--author", "--user", "--member"]):
            raise commands.ArgParserFailure("--scope", _("Nothing"), custom_help=_(_USER_HELP))

        target_scope: Optional[str] = target_scope or None
        target_user: Union[discord.Member, discord.User] = target_user or ctx.author
        target_guild: discord.Guild = target_guild or ctx.guild

        return target_scope, target_user, target_guild, specified_user