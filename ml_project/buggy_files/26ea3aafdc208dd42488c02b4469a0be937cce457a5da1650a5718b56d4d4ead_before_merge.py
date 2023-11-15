    async def message_content(self, embed: bool = True):
        """
        Format a case message

        Parameters
        ----------
        embed: bool
            Whether or not to get an embed

        Returns
        -------
        discord.Embed or `str`
            A rich embed or string representing a case message

        """
        casetype = await get_casetype(self.action_type)
        title = "{}".format(
            _("Case #{} | {} {}").format(self.case_number, casetype.case_str, casetype.image)
        )

        if self.reason:
            reason = _("**Reason:** {}").format(self.reason)
        else:
            reason = _("**Reason:** Use the `reason` command to add it")

        if self.moderator is not None:
            moderator = escape_spoilers(f"{self.moderator} ({self.moderator.id})")
        else:
            moderator = _("Unknown")
        until = None
        duration = None
        if self.until:
            start = datetime.fromtimestamp(self.created_at)
            end = datetime.fromtimestamp(self.until)
            end_fmt = end.strftime("%Y-%m-%d %H:%M:%S")
            duration = end - start
            dur_fmt = _strfdelta(duration)
            until = end_fmt
            duration = dur_fmt

        amended_by = None
        if self.amended_by:
            amended_by = escape_spoilers(
                "{}#{} ({})".format(
                    self.amended_by.name, self.amended_by.discriminator, self.amended_by.id
                )
            )

        last_modified = None
        if self.modified_at:
            last_modified = "{}".format(
                datetime.fromtimestamp(self.modified_at).strftime("%Y-%m-%d %H:%M:%S")
            )

        if isinstance(self.user, int):
            if self.last_known_username is None:
                user = f"[Unknown or Deleted User] ({self.user})"
            else:
                user = f"{self.last_known_username} ({self.user})"
            avatar_url = None
        else:
            user = escape_spoilers(
                filter_invites(f"{self.user} ({self.user.id})")
            )  # Invites and spoilers get rendered even in embeds.
            avatar_url = self.user.avatar_url

        if embed:
            emb = discord.Embed(title=title, description=reason)
            emb.set_author(name=user)
            emb.add_field(name=_("Moderator"), value=moderator, inline=False)
            if until and duration:
                emb.add_field(name=_("Until"), value=until)
                emb.add_field(name=_("Duration"), value=duration)

            if isinstance(self.channel, int):
                emb.add_field(
                    name=_("Channel"),
                    value=_("{channel} (deleted)").format(channel=self.channel),
                    inline=False,
                )
            elif self.channel is not None:
                emb.add_field(name=_("Channel"), value=self.channel.name, inline=False)
            if amended_by:
                emb.add_field(name=_("Amended by"), value=amended_by)
            if last_modified:
                emb.add_field(name=_("Last modified at"), value=last_modified)
            emb.timestamp = datetime.fromtimestamp(self.created_at)
            return emb
        else:
            user = filter_mass_mentions(filter_urls(user))  # Further sanitization outside embeds
            case_text = ""
            case_text += "{}\n".format(title)
            case_text += _("**User:** {}\n").format(user)
            case_text += _("**Moderator:** {}\n").format(moderator)
            case_text += "{}\n".format(reason)
            if until and duration:
                case_text += _("**Until:** {}\n**Duration:** {}\n").format(until, duration)
            if self.channel:
                case_text += _("**Channel**: {}\n").format(self.channel.name)
            if amended_by:
                case_text += _("**Amended by:** {}\n").format(amended_by)
            if last_modified:
                case_text += _("**Last modified at:** {}\n").format(last_modified)
            return case_text.strip()