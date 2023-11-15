    async def __call__(
        self,
        parent_result: Optional[Any],
        args: Dict[str, Any],
        ctx: Optional[Dict[str, Any]],
        info: "Info",
    ) -> (Any, Any):
        try:
            default_args = self._schema_field.get_arguments_default_values()
            default_args.update(
                {argument.name: argument.value for argument in args.values()}
            )

            result = await self._func(parent_result, default_args, ctx, info)
            if info.execution_ctx.is_introspection:
                result = await self._introspection(result, ctx, info)
            return result, self._coercer(result, info)
        except Exception as e:  # pylint: disable=broad-except
            return e, None