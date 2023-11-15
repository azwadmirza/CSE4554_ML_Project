    def grideditor_save(self, path: mitmproxy.types.Path) -> None:
        """
            Save data to file as a CSV.
        """
        rows = self._grideditor().value
        try:
            with open(path, "w", newline='', encoding="utf8") as fp:
                writer = csv.writer(fp)
                for row in rows:
                    writer.writerow(
                        [strutils.always_str(x) or "" for x in row]  # type: ignore
                    )
            ctx.log.alert("Saved %s rows as CSV." % (len(rows)))
        except IOError as e:
            ctx.log.error(str(e))