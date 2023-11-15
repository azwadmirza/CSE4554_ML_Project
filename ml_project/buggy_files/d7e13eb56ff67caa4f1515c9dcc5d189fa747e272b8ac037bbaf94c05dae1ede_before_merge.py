    async def _set(self, ctx: commands.Context, to: discord.Member, creds: SetParser):
        """Set the balance of user's bank account.

        Passing positive and negative values will add/remove currency instead.

        Examples:
        - `[p]bank set @Twentysix 26` - Sets balance to 26
        - `[p]bank set @Twentysix +2` - Increases balance by 2
        - `[p]bank set @Twentysix -6` - Decreases balance by 6
        """
        author = ctx.author
        currency = await bank.get_currency_name(ctx.guild)

        if creds.operation == "deposit":
            await bank.deposit_credits(to, creds.sum)
            await ctx.send(
                _("{author} added {num} {currency} to {user}'s account.").format(
                    author=author.display_name,
                    num=creds.sum,
                    currency=currency,
                    user=to.display_name,
                )
            )
        elif creds.operation == "withdraw":
            await bank.withdraw_credits(to, creds.sum)
            await ctx.send(
                _("{author} removed {num} {currency} from {user}'s account.").format(
                    author=author.display_name,
                    num=creds.sum,
                    currency=currency,
                    user=to.display_name,
                )
            )
        else:
            await bank.set_balance(to, creds.sum)
            await ctx.send(
                _("{author} set {user}'s account balance to {num} {currency}.").format(
                    author=author.display_name,
                    num=creds.sum,
                    currency=currency,
                    user=to.display_name,
                )
            )