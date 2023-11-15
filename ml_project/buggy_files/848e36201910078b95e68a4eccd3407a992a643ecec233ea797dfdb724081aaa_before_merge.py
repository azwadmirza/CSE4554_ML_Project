    async def _show_form(
        self, step="user", placeholders=None, errors=None, data_schema=None
    ) -> None:
        """Show the form to the user."""
        _LOGGER.debug("show_form %s %s %s %s", step, placeholders, errors, data_schema)
        data_schema = data_schema or vol.Schema(self.data_schema)
        return self.async_show_form(
            step_id=step,
            data_schema=data_schema,
            errors=errors if errors else {},
            description_placeholders=placeholders if placeholders else {},
        )