    async def _eq_delete(self, ctx: commands.Context, eq_preset: str):
        """Delete a saved eq preset."""
        async with self.config.custom("EQUALIZER", ctx.guild.id).eq_presets() as eq_presets:
            eq_preset = eq_preset.lower()
            try:
                if eq_presets[eq_preset][
                    "author"
                ] != ctx.author.id and not await self._can_instaskip(ctx, ctx.author):
                    return await self._embed_msg(
                        ctx, _("You are not the author of that preset setting.")
                    )
                del eq_presets[eq_preset]
            except KeyError:
                return await self._embed_msg(
                    ctx,
                    _(
                        "{eq_preset} is not in the eq preset list.".format(
                            eq_preset=eq_preset.capitalize()
                        )
                    ),
                )
            except TypeError:
                if await self._can_instaskip(ctx, ctx.author):
                    del eq_presets[eq_preset]
                else:
                    return await self._embed_msg(
                        ctx, _("You are not the author of that preset setting.")
                    )

        await self._embed_msg(
            ctx, _("The {preset_name} preset was deleted.".format(preset_name=eq_preset))
        )