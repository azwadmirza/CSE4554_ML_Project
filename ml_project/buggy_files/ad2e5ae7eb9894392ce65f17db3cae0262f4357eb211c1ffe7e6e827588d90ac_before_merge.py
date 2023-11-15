    async def imgurcreds(self, ctx, imgur_client_id: str):
        """Sets the imgur client id
        You will need an account on Imgur to get this

        You can get these by visiting https://api.imgur.com/oauth2/addclient
        and filling out the form. Enter a name for the application, select
        'Anonymous usage without user authorization' for the auth type,
        leave the app website blank, enter a valid email address, and
        enter a description. Check the box for the captcha, then click Next.
        Your client ID will be on the page that loads"""
        await self.settings.imgur_client_id.set(imgur_client_id)
        await ctx.send(_("Set the imgur client id!"))