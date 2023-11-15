    async def _embed_msg(ctx: commands.Context, title: str):
        embed = discord.Embed(colour=await ctx.embed_colour(), title=title)
        await ctx.send(embed=embed)