    async def setup(self, *, creator=None, category=None, initial_message=None):
        """Create the thread channel and other io related initialisation tasks"""
        self.bot.dispatch("thread_initiate", self)
        recipient = self.recipient

        # in case it creates a channel outside of category
        overwrites = {
            self.bot.modmail_guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }

        category = category or self.bot.main_category

        if category is not None:
            overwrites = None

        try:
            channel = await self.bot.modmail_guild.create_text_channel(
                name=format_channel_name(recipient, self.bot.modmail_guild),
                category=category,
                overwrites=overwrites,
                reason="Creating a thread channel.",
            )
        except discord.HTTPException as e:
            # try again but null-discrim (name could be banned)
            try:
                channel = await self.bot.modmail_guild.create_text_channel(
                    name=format_channel_name(recipient, self.bot.modmail_guild, force_null=True),
                    category=category,
                    overwrites=overwrites,
                    reason="Creating a thread channel.",
                )
            except discord.HTTPException as e:  # Failed to create due to missing perms.
                logger.critical("An error occurred while creating a thread.", exc_info=True)
                self.manager.cache.pop(self.id)

                embed = discord.Embed(color=self.bot.error_color)
                embed.title = "Error while trying to create a thread."
                embed.description = str(e)
                embed.add_field(name="Recipient", value=recipient.mention)

                if self.bot.log_channel is not None:
                    await self.bot.log_channel.send(embed=embed)
                return

        self._channel = channel

        try:
            log_url, log_data = await asyncio.gather(
                self.bot.api.create_log_entry(recipient, channel, creator or recipient),
                self.bot.api.get_user_logs(recipient.id),
            )

            log_count = sum(1 for log in log_data if not log["open"])
        except Exception:
            logger.error("An error occurred while posting logs to the database.", exc_info=True)
            log_url = log_count = None
            # ensure core functionality still works

        await channel.edit(topic=f"User ID: {recipient.id}")
        self.ready = True

        if creator is not None and creator != recipient:
            mention = None
        else:
            mention = self.bot.config["mention"]

        async def send_genesis_message():
            info_embed = self._format_info_embed(
                recipient, log_url, log_count, self.bot.main_color
            )
            try:
                msg = await channel.send(mention, embed=info_embed)
                self.bot.loop.create_task(msg.pin())
                self.genesis_message = msg
            except Exception:
                logger.error("Failed unexpectedly:", exc_info=True)

        async def send_recipient_genesis_message():
            # Once thread is ready, tell the recipient.
            thread_creation_response = self.bot.config["thread_creation_response"]

            embed = discord.Embed(
                color=self.bot.mod_color,
                description=thread_creation_response,
                timestamp=channel.created_at,
            )

            recipient_thread_close = self.bot.config.get("recipient_thread_close")

            if recipient_thread_close:
                footer = self.bot.config["thread_self_closable_creation_footer"]
            else:
                footer = self.bot.config["thread_creation_footer"]

            embed.set_footer(text=footer, icon_url=self.bot.guild.icon_url)
            embed.title = self.bot.config["thread_creation_title"]

            if creator is None or creator == recipient:
                msg = await recipient.send(embed=embed)

                if recipient_thread_close:
                    close_emoji = self.bot.config["close_emoji"]
                    close_emoji = await self.bot.convert_emoji(close_emoji)
                    await self.bot.add_reaction(msg, close_emoji)

        async def send_persistent_notes():
            notes = await self.bot.api.find_notes(self.recipient)
            ids = {}

            class State:
                def store_user(self, user):
                    return user

            for note in notes:
                author = note["author"]

                class Author:
                    name = author["name"]
                    id = author["id"]
                    discriminator = author["discriminator"]
                    avatar_url = author["avatar_url"]

                data = {
                    "id": round(time.time() * 1000 - discord.utils.DISCORD_EPOCH) << 22,
                    "attachments": {},
                    "embeds": {},
                    "edited_timestamp": None,
                    "type": None,
                    "pinned": None,
                    "mention_everyone": None,
                    "tts": None,
                    "content": note["message"],
                    "author": Author(),
                }
                message = discord.Message(state=State(), channel=None, data=data)
                ids[note["_id"]] = str(
                    (await self.note(message, persistent=True, thread_creation=True)).id
                )

            await self.bot.api.update_note_ids(ids)

        async def activate_auto_triggers():
            message = DummyMessage(copy.copy(initial_message))
            if message:
                try:
                    return await self.bot.trigger_auto_triggers(message, channel)
                except RuntimeError:
                    pass

        await asyncio.gather(
            send_genesis_message(),
            send_recipient_genesis_message(),
            activate_auto_triggers(),
            send_persistent_notes(),
        )
        self.bot.dispatch("thread_ready", self)