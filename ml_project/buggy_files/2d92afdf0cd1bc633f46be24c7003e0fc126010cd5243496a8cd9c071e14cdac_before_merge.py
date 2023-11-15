def split_file(filepath, output_dir, docs_per_file=1_000, delimiter="", encoding="utf-8"):
    total_lines = sum(1 for line in open(filepath, encoding=encoding))
    output_file_number = 1
    doc_count = 0
    lines_to_write = []
    with ExitStack() as stack:
        input_file = stack.enter_context(open(filepath, 'r', encoding=encoding))
        for line_num, line in enumerate(tqdm(input_file, desc="Splitting file ...", total=total_lines)):
            lines_to_write.append(line)
            if line.strip() == delimiter:
                doc_count += 1
                if doc_count % docs_per_file == 0:
                    filename = output_dir / f"part_{output_file_number}"
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    write_file = stack.enter_context(open(filename, 'w+', buffering=10 * 1024 * 1024))
                    write_file.writelines(lines_to_write)
                    write_file.close()
                    output_file_number += 1
                    lines_to_write = []

        if lines_to_write:
            filename = output_dir / f"part_{output_file_number}"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            write_file = stack.enter_context(open(filename, 'w+', buffering=10 * 1024 * 1024))
            write_file.writelines(lines_to_write)
            write_file.close()

    logger.info(f"The input file {filepath} is split in {output_file_number} parts at {output_dir}.")