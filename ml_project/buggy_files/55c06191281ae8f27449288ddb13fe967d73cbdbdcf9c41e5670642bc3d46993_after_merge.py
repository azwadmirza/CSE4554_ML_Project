def ls(long: bool, dropbox_path: str, include_deleted: bool, config_name: str) -> None:

    from datetime import datetime
    from .utils import natural_size

    if not dropbox_path.startswith("/"):
        dropbox_path = "/" + dropbox_path

    with MaestralProxy(config_name, fallback=True) as m:

        entries = m.list_folder(
            dropbox_path,
            recursive=False,
            include_deleted=include_deleted,
        )
        entries.sort(key=lambda x: cast(str, x["name"]).lower())

        if long:

            names = []
            types = []
            sizes = []
            shared = []
            last_modified = []
            excluded = []

            to_short_type = {
                "FileMetadata": "file",
                "FolderMetadata": "folder",
                "DeletedMetadata": "deleted",
            }

            for e in entries:

                long_type = cast(str, e["type"])
                name = cast(str, e["name"])
                path_lower = cast(str, e["path_lower"])

                types.append(to_short_type[long_type])
                names.append(name)

                shared.append("shared" if "sharing_info" in e else "private")
                excluded.append(m.excluded_status(path_lower))

                if "size" in e:
                    size = cast(float, e["size"])
                    sizes.append(natural_size(size))
                else:
                    sizes.append("-")

                if "client_modified" in e:
                    cm = cast(str, e["client_modified"])
                    dt = datetime.strptime(cm, "%Y-%m-%dT%H:%M:%S%z").astimezone()
                    last_modified.append(dt.strftime("%d %b %Y %H:%M"))
                else:
                    last_modified.append("-")

            click.echo("")
            click.echo(
                format_table(
                    headers=["Name", "Type", "Size", "Shared", "Syncing", "Modified"],
                    columns=[names, types, sizes, shared, excluded, last_modified],
                    alignment=[LEFT, LEFT, RIGHT, LEFT, LEFT, LEFT],
                    wrap=False,
                ),
            )
            click.echo("")

        else:

            from .utils import chunks

            names = []
            colors = []
            formatted_names = []
            max_len = 0

            for e in entries:
                name = cast(str, e["name"])

                max_len = max(max_len, len(name))
                names.append(name)
                colors.append("blue" if e["type"] == "DeletedMetadata" else None)

            max_len += 2  # add 2 spaces padding

            for name, color in zip(names, colors):
                formatted_names.append(click.style(name.ljust(max_len), fg=color))

            width, height = click.get_terminal_size()
            n_columns = max(width // max_len, 1)

            rows = chunks(formatted_names, n_columns)

            for row in rows:
                click.echo("".join(row))