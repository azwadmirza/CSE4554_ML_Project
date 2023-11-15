    async def backup(self, ctx, backup_path: str = None):
        """Creates a backup of all data for the instance."""
        from redbot.core.data_manager import basic_config, instance_name
        from redbot.core.drivers.red_json import JSON

        data_dir = Path(basic_config["DATA_PATH"])
        if basic_config["STORAGE_TYPE"] == "MongoDB":
            from redbot.core.drivers.red_mongo import Mongo

            m = Mongo("Core", **basic_config["STORAGE_DETAILS"])
            db = m.db
            collection_names = await db.collection_names(include_system_collections=False)
            for c_name in collection_names:
                if c_name == "Core":
                    c_data_path = data_dir / basic_config["CORE_PATH_APPEND"]
                else:
                    c_data_path = data_dir / basic_config["COG_PATH_APPEND"]
                output = {}
                docs = await db[c_name].find().to_list(None)
                for item in docs:
                    item_id = str(item.pop("_id"))
                    output[item_id] = item
                target = JSON(c_name, data_path_override=c_data_path)
                await target.jsonIO._threadsafe_save_json(output)
        backup_filename = "redv3-{}-{}.tar.gz".format(
            instance_name, ctx.message.created_at.strftime("%Y-%m-%d %H-%M-%S")
        )
        if data_dir.exists():
            if not backup_path:
                backup_pth = data_dir.home()
            else:
                backup_pth = Path(backup_path)
            backup_file = backup_pth / backup_filename

            to_backup = []
            exclusions = [
                "__pycache__",
                "Lavalink.jar",
                os.path.join("Downloader", "lib"),
                os.path.join("CogManager", "cogs"),
                os.path.join("RepoManager", "repos"),
            ]
            downloader_cog = ctx.bot.get_cog("Downloader")
            if downloader_cog and hasattr(downloader_cog, "_repo_manager"):
                repo_output = []
                repo_mgr = downloader_cog._repo_manager
                for n, repo in repo_mgr._repos:
                    repo_output.append(
                        {{"url": repo.url, "name": repo.name, "branch": repo.branch}}
                    )
                repo_filename = data_dir / "cogs" / "RepoManager" / "repos.json"
                with open(str(repo_filename), "w") as f:
                    f.write(json.dumps(repo_output, indent=4))
            instance_data = {instance_name: basic_config}
            instance_file = data_dir / "instance.json"
            with open(str(instance_file), "w") as instance_out:
                instance_out.write(json.dumps(instance_data, indent=4))
            for f in data_dir.glob("**/*"):
                if not any(ex in str(f) for ex in exclusions):
                    to_backup.append(f)
            with tarfile.open(str(backup_file), "w:gz") as tar:
                for f in to_backup:
                    tar.add(str(f), recursive=False)
            print(str(backup_file))
            await ctx.send(
                _("A backup has been made of this instance. It is at {}.").format((backup_file))
            )
            await ctx.send(_("Would you like to receive a copy via DM? (y/n)"))

            def same_author_check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await ctx.bot.wait_for("message", check=same_author_check, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send(_("Ok then."))
            else:
                if msg.content.lower().strip() == "y":
                    await ctx.author.send(
                        _("Here's a copy of the backup"), file=discord.File(str(backup_file))
                    )
        else:
            await ctx.send(_("That directory doesn't seem to exist..."))