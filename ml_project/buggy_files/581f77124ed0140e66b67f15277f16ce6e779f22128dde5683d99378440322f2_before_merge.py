    async def rolepaydayamount(self, ctx: commands.Context, role: discord.Role, creds: int):
        """Set the amount earned each payday for a role."""
        guild = ctx.guild
        credits_name = await bank.get_currency_name(guild)
        if await bank.is_global():
            await ctx.send(_("The bank must be per-server for per-role paydays to work."))
        else:
            await self.config.role(role).PAYDAY_CREDITS.set(creds)
            await ctx.send(
                _(
                    "Every payday will now give {num} {currency} "
                    "to people with the role {role_name}."
                ).format(num=creds, currency=credits_name, role_name=role.name)
            )