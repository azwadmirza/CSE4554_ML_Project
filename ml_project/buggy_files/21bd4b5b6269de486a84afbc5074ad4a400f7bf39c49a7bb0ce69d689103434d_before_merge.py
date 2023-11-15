    async def _skip_action(ctx):
        player = lavalink.get_player(ctx.guild.id)
        if not player.queue:
            pos, dur = player.position, player.current.length
            time_remain = lavalink.utils.format_time(dur - pos)
            if player.current.is_stream:
                embed = discord.Embed(
                    colour=ctx.guild.me.top_role.colour, title="There's nothing in the queue."
                )
                embed.set_footer(text="Currently livestreaming {}".format(player.current.title))
            else:
                embed = discord.Embed(
                    colour=ctx.guild.me.top_role.colour, title="There's nothing in the queue."
                )
                embed.set_footer(text="{} left on {}".format(time_remain, player.current.title))
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            colour=ctx.guild.me.top_role.colour,
            title="Track Skipped",
            description="**[{}]({})**".format(player.current.title, player.current.uri),
        )
        await ctx.send(embed=embed)
        await player.skip()