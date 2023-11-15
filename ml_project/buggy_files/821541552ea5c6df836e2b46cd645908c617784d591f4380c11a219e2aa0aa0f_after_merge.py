    async def check_streams(self):
        for stream in self.streams:
            try:
                try:
                    is_rerun = False
                    is_schedule = False
                    if stream.__class__.__name__ == "TwitchStream":
                        await self.maybe_renew_twitch_bearer_token()
                        embed, is_rerun = await stream.is_online()

                    elif stream.__class__.__name__ == "YoutubeStream":
                        embed, is_schedule = await stream.is_online()

                    else:
                        embed = await stream.is_online()
                except OfflineStream:
                    if not stream._messages_cache:
                        continue
                    for message in stream._messages_cache:
                        if await self.bot.cog_disabled_in_guild(self, message.guild):
                            continue
                        autodelete = await self.config.guild(message.guild).autodelete()
                        if autodelete:
                            with contextlib.suppress(discord.NotFound):
                                await message.delete()
                    stream._messages_cache.clear()
                    await self.save_streams()
                else:
                    if stream._messages_cache:
                        continue
                    for channel_id in stream.channels:
                        channel = self.bot.get_channel(channel_id)
                        if not channel:
                            continue
                        if await self.bot.cog_disabled_in_guild(self, channel.guild):
                            continue
                        ignore_reruns = await self.config.guild(channel.guild).ignore_reruns()
                        if ignore_reruns and is_rerun:
                            continue
                        ignore_schedules = await self.config.guild(channel.guild).ignore_schedule()
                        if ignore_schedules and is_schedule:
                            continue
                        if is_schedule:
                            # skip messages and mentions
                            await self._send_stream_alert(stream, channel, embed)
                            await self.save_streams()
                            continue
                        await set_contextual_locales_from_guild(self.bot, channel.guild)

                        mention_str, edited_roles = await self._get_mention_str(
                            channel.guild, channel
                        )

                        if mention_str:
                            alert_msg = await self.config.guild(
                                channel.guild
                            ).live_message_mention()
                            if alert_msg:
                                content = alert_msg  # Stop bad things from happening here...
                                content = content.replace(
                                    "{stream.name}", str(stream.name)
                                )  # Backwards compatibility
                                content = content.replace("{stream}", str(stream.name))
                                content = content.replace("{mention}", mention_str)
                            else:
                                content = _("{mention}, {stream} is live!").format(
                                    mention=mention_str,
                                    stream=escape(
                                        str(stream.name), mass_mentions=True, formatting=True
                                    ),
                                )
                        else:
                            alert_msg = await self.config.guild(
                                channel.guild
                            ).live_message_nomention()
                            if alert_msg:
                                content = alert_msg  # Stop bad things from happening here...
                                content = content.replace(
                                    "{stream.name}", str(stream.name)
                                )  # Backwards compatibility
                                content = content.replace("{stream}", str(stream.name))
                            else:
                                content = _("{stream} is live!").format(
                                    stream=escape(
                                        str(stream.name), mass_mentions=True, formatting=True
                                    )
                                )
                        await self._send_stream_alert(stream, channel, embed, content)
                        if edited_roles:
                            for role in edited_roles:
                                await role.edit(mentionable=False)
                        await self.save_streams()
            except Exception as e:
                log.error("An error has occured with Streams. Please report it.", exc_info=e)