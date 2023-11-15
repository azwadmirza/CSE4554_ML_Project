    async def notify_user(
        self,
        current: int = None,
        total: int = None,
        key: str = None,
        seconds_key: str = None,
        seconds: str = None,
    ):
        """This updates an existing message.

        Based on the message found in :variable:`Notifier.updates` as per the `key` param
        """
        if self.last_msg_time + self.cooldown > time.time() and not current == total:
            return
        if self.color is None:
            self.color = await self.context.embed_colour()
        embed2 = discord.Embed(
            colour=self.color,
            title=self.updates.get(key, "").format(num=current, total=total, seconds=seconds),
        )
        if seconds and seconds_key:
            embed2.set_footer(text=self.updates.get(seconds_key, "").format(seconds=seconds))
        try:
            await self.message.edit(embed=embed2)
            self.last_msg_time = int(time.time())
        except discord.errors.NotFound:
            pass