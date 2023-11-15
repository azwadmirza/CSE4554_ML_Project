def fix_invalid_folder_locations(out_dir: str=OUTPUT_DIR) -> Tuple[List[str], List[str]]:
    fixed = []
    cant_fix = []
    for entry in os.scandir(os.path.join(out_dir, ARCHIVE_DIR_NAME)):
        if entry.is_dir(follow_symlinks=True):
            if os.path.exists(os.path.join(entry.path, 'index.json')):
                try:
                    link = parse_json_link_details(entry.path)
                except KeyError:
                    link = None
                if not link:
                    continue

                if not entry.path.endswith(f'/{link.timestamp}'):
                    dest = os.path.join(out_dir, ARCHIVE_DIR_NAME, link.timestamp)
                    if os.path.exists(dest):
                        cant_fix.append(entry.path)
                    else:
                        shutil.move(entry.path, dest)
                        fixed.append(dest)
                        timestamp = entry.path.rsplit('/', 1)[-1]
                        assert link.link_dir == entry.path
                        assert link.timestamp == timestamp
                        write_json_link_details(link, out_dir=entry.path)

    return fixed, cant_fix