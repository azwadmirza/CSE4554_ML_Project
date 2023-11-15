def save_readability(link: Link, out_dir: Optional[str]=None, timeout: int=TIMEOUT) -> ArchiveResult:
    """download reader friendly version using @mozilla/readability"""

    out_dir = Path(out_dir or link.link_dir)
    output_folder = out_dir.absolute() / "readability"
    output = str(output_folder)

    # Readability Docs: https://github.com/mozilla/readability

    status = 'succeeded'
    timer = TimedProgress(timeout, prefix='      ')
    try:
        document = get_html(link, out_dir)
        temp_doc = NamedTemporaryFile(delete=False)
        temp_doc.write(document.encode("utf-8"))
        temp_doc.close()

        cmd = [
            DEPENDENCIES['READABILITY_BINARY']['path'],
            temp_doc.name
        ]

        result = run(cmd, cwd=out_dir, timeout=timeout)
        result_json = json.loads(result.stdout)
        output_folder.mkdir(exist_ok=True)
        atomic_write(str(output_folder / "content.html"), result_json.pop("content"))
        atomic_write(str(output_folder / "content.txt"), result_json.pop("textContent"))
        atomic_write(str(output_folder / "article.json"), result_json)

        # parse out number of files downloaded from last line of stderr:
        #  "Downloaded: 76 files, 4.0M in 1.6s (2.52 MB/s)"
        output_tail = [
            line.strip()
            for line in (result.stdout + result.stderr).decode().rsplit('\n', 3)[-3:]
            if line.strip()
        ]
        hints = (
            'Got readability response code: {}.'.format(result.returncode),
            *output_tail,
        )

        # Check for common failure cases
        if (result.returncode > 0):
            raise ArchiveError('Readability was not able to archive the page', hints)
    except (Exception, OSError) as err:
        status = 'failed'
        output = err
    finally:
        timer.end()

    return ArchiveResult(
        cmd=cmd,
        pwd=str(out_dir),
        cmd_version=READABILITY_VERSION,
        output=output,
        status=status,
        **timer.stats,
    )