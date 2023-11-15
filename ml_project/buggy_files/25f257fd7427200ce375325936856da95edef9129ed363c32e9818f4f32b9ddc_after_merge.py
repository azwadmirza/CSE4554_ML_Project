    async def __call__(
        self,
        parent_result: Optional[Any],
        args: Dict[str, Any],
        ctx: Optional[Dict[str, Any]],
        info: "Info",
    ) -> (Any, Any):
        try:
            result = await self._func(
                parent_result,
                await coerce_arguments(
                    self._schema_field.arguments, args, ctx, info
                ),
                ctx,
                info,
            )

            if info.execution_ctx.is_introspection:
                result = await self._introspection(result, ctx, info)
            return result, self._coercer(result, info)
        except Exception as e:  # pylint: disable=broad-except
            return e, None