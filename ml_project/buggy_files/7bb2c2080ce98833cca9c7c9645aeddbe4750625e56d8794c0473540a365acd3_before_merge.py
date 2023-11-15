    def save(
        self,
        flows: typing.Sequence[flow.Flow],
        cuts: mitmproxy.types.CutSpec,
        path: mitmproxy.types.Path
    ) -> None:
        """
            Save cuts to file. If there are multiple flows or cuts, the format
            is UTF-8 encoded CSV. If there is exactly one row and one column,
            the data is written to file as-is, with raw bytes preserved. If the
            path is prefixed with a "+", values are appended if there is an
            existing file.
        """
        append = False
        if path.startswith("+"):
            append = True
            path = mitmproxy.types.Path(path[1:])
        if len(cuts) == 1 and len(flows) == 1:
            with open(path, "ab" if append else "wb") as fp:
                if fp.tell() > 0:
                    # We're appending to a file that already exists and has content
                    fp.write(b"\n")
                v = extract(cuts[0], flows[0])
                if isinstance(v, bytes):
                    fp.write(v)
                else:
                    fp.write(v.encode("utf8"))
            ctx.log.alert("Saved single cut.")
        else:
            with open(path, "a" if append else "w", newline='', encoding="utf8") as fp:
                writer = csv.writer(fp)
                for f in flows:
                    vals = [extract(c, f) for c in cuts]
                    writer.writerow(
                        [strutils.always_str(x) or "" for x in vals]  # type: ignore
                    )
            ctx.log.alert("Saved %s cuts over %d flows as CSV." % (len(cuts), len(flows)))