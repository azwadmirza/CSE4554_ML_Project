    async def update_embed(self, embed: discord.Embed):
        try:
            await self.message.edit(embed=embed)
            self.last_msg_time = int(time.time())
        except discord.errors.NotFound:
            pass