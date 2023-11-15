    def clip(
        self,
        flows: typing.Sequence[flow.Flow],
        cuts: mitmproxy.types.CutSpec,
    ) -> None:
        """
            Send cuts to the clipboard. If there are multiple flows or cuts, the
            format is UTF-8 encoded CSV. If there is exactly one row and one
            column, the data is written to file as-is, with raw bytes preserved.
        """
        fp = io.StringIO(newline="")
        if len(cuts) == 1 and len(flows) == 1:
            v = extract(cuts[0], flows[0])
            if isinstance(v, bytes):
                fp.write(strutils.always_str(v))
            else:
                fp.write("utf8")
            ctx.log.alert("Clipped single cut.")
        else:
            writer = csv.writer(fp)
            for f in flows:
                vals = [extract(c, f) for c in cuts]
                writer.writerow(
                    [strutils.always_str(v) or "" for v in vals]  # type: ignore
                )
            ctx.log.alert("Clipped %s cuts as CSV." % len(cuts))
        try:
            pyperclip.copy(fp.getvalue())
        except pyperclip.PyperclipException as e:
            ctx.log.error(str(e))