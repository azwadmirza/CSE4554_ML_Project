    async def allowed_by_whitelist_blacklist(
        self,
        who: Optional[Union[discord.Member, discord.User]] = None,
        *,
        who_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        role_ids: Optional[List[int]] = None,
    ) -> bool:
        """
        This checks if a user or member is allowed to run things,
        as considered by Red's whitelist and blacklist.

        If given a user object, this function will check the global lists

        If given a member, this will additionally check guild lists

        If omiting a user or member, you must provide a value for ``who_id``

        You may also provide a value for ``guild_id`` in this case

        If providing a member by guild and member ids,
        you should supply ``role_ids`` as well

        Parameters
        ----------
        who : Optional[Union[discord.Member, discord.User]]
            The user or member object to check

        Other Parameters
        ----------------
        who_id : Optional[int]
            The id of the user or member to check
            If not providing a value for ``who``, this is a required parameter.
        guild_id : Optional[int]
            When used in conjunction with a provided value for ``who_id``, checks
            the lists for the corresponding guild as well.
        role_ids : Optional[List[int]]
            When used with both ``who_id`` and ``guild_id``, checks the role ids provided.
            This is required for accurate checking of members in a guild if providing ids.

        Raises
        ------
        TypeError
            Did not provide ``who`` or ``who_id``

        Returns
        -------
        bool
            `True` if user is allowed to run things, `False` otherwise
        """
        # Contributor Note:
        # All config calls are delayed until needed in this section
        # All changes should be made keeping in mind that this is also used as a global check

        guild = None
        mocked = False  # used for an accurate delayed role id expansion later.
        if not who:
            if not who_id:
                raise TypeError("Must provide a value for either `who` or `who_id`")
            mocked = True
            who = discord.Object(id=who_id)
            if guild_id:
                guild = discord.Object(id=guild_id)
        else:
            guild = getattr(who, "guild", None)

        if await self.is_owner(who):
            return True

        global_whitelist = await self._whiteblacklist_cache.get_whitelist()
        if global_whitelist:
            if who.id not in global_whitelist:
                return False
        else:
            # blacklist is only used when whitelist doesn't exist.
            global_blacklist = await self._whiteblacklist_cache.get_blacklist()
            if who.id in global_blacklist:
                return False

        if guild:
            if guild.owner_id == who.id:
                return True

            # The delayed expansion of ids to check saves time in the DM case.
            # Converting to a set reduces the total lookup time in section
            if mocked:
                ids = {i for i in (who.id, *(role_ids or [])) if i != guild.id}
            else:
                # DEP-WARN
                # This uses member._roles (getattr is for the user case)
                # If this is removed upstream (undocumented)
                # there is a silent failure potential, and role blacklist/whitelists will break.
                ids = {i for i in (who.id, *(getattr(who, "_roles", []))) if i != guild.id}

            guild_whitelist = await self._whiteblacklist_cache.get_whitelist(guild)
            if guild_whitelist:
                if ids.isdisjoint(guild_whitelist):
                    return False
            else:
                guild_blacklist = await self._whiteblacklist_cache.get_blacklist(guild)
                if not ids.isdisjoint(guild_blacklist):
                    return False

        return True