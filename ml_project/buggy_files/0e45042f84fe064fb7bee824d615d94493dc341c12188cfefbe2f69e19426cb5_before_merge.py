    async def payday(self, ctx: commands.Context):
        """Get some free currency."""
        author = ctx.author
        guild = ctx.guild

        cur_time = calendar.timegm(ctx.message.created_at.utctimetuple())
        credits_name = await bank.get_currency_name(ctx.guild)
        if await bank.is_global():  # Role payouts will not be used
            next_payday = await self.config.user(author).next_payday()
            if cur_time >= next_payday:
                await bank.deposit_credits(author, await self.config.PAYDAY_CREDITS())
                next_payday = cur_time + await self.config.PAYDAY_TIME()
                await self.config.user(author).next_payday.set(next_payday)

                pos = await bank.get_leaderboard_position(author)
                await ctx.send(
                    _(
                        "{author.mention} Here, take some {currency}. "
                        "Enjoy! (+{amount} {currency}!)\n\n"
                        "You currently have {new_balance} {currency}.\n\n"
                        "You are currently #{pos} on the global leaderboard!"
                    ).format(
                        author=author,
                        currency=credits_name,
                        amount=await self.config.PAYDAY_CREDITS(),
                        new_balance=await bank.get_balance(author),
                        pos=pos,
                    )
                )

            else:
                dtime = self.display_time(next_payday - cur_time)
                await ctx.send(
                    _(
                        "{author.mention} Too soon. For your next payday you have to wait {time}."
                    ).format(author=author, time=dtime)
                )
        else:
            next_payday = await self.config.member(author).next_payday()
            if cur_time >= next_payday:
                credit_amount = await self.config.guild(guild).PAYDAY_CREDITS()
                for role in author.roles:
                    role_credits = await self.config.role(
                        role
                    ).PAYDAY_CREDITS()  # Nice variable name
                    if role_credits > credit_amount:
                        credit_amount = role_credits
                await bank.deposit_credits(author, credit_amount)
                next_payday = cur_time + await self.config.guild(guild).PAYDAY_TIME()
                await self.config.member(author).next_payday.set(next_payday)
                pos = await bank.get_leaderboard_position(author)
                await ctx.send(
                    _(
                        "{author.mention} Here, take some {currency}. "
                        "Enjoy! (+{amount} {new_balance}!)\n\n"
                        "You currently have {new_balance} {currency}.\n\n"
                        "You are currently #{pos} on the global leaderboard!"
                    ).format(
                        author=author,
                        currency=credits_name,
                        amount=credit_amount,
                        new_balance=await bank.get_balance(author),
                        pos=pos,
                    )
                )
            else:
                dtime = self.display_time(next_payday - cur_time)
                await ctx.send(
                    _(
                        "{author.mention} Too soon. For your next payday you have to wait {time}."
                    ).format(author=author, time=dtime)
                )