    def register_sdl(
        schema_name: str,
        sdl: Union[str, List[str], GraphQLSchema],
        exclude_builtins_scalars: Optional[List[str]] = None,
    ) -> None:
        SchemaRegistry._schemas.setdefault(schema_name, {})

        # Maybe read them one and use them a lot :p
        sdl_files_list = _get_builtins_sdl_files(exclude_builtins_scalars)

        full_sdl = ""

        if isinstance(sdl, list):
            sdl_files_list += sdl
        elif os.path.isfile(sdl):
            sdl_files_list.append(sdl)
        elif os.path.isdir(sdl):
            sdl_files_list += glob(
                os.path.join(sdl, "**/*.sdl"), recursive=True
            ) + glob(os.path.join(sdl, "**/*.graphql"), recursive=True)
        else:
            full_sdl = sdl

        # Convert SDL files into big schema and parse it
        for filepath in sdl_files_list:
            with open(filepath, "r") as sdl_file:
                full_sdl += " " + sdl_file.read().replace("\n", " ")

        SchemaRegistry._schemas[schema_name]["sdl"] = full_sdl