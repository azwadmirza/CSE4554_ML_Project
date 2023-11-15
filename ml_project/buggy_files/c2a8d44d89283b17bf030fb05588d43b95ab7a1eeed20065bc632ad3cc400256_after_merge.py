def main():
    args = argument_parser()

    ecs_version = read_version(args.ref)
    print('Running generator. ECS version ' + ecs_version)

    # default location to save files
    out_dir = 'generated'
    docs_dir = 'docs'
    if args.out:
        default_dirs = False
        out_dir = os.path.join(args.out, out_dir)
        docs_dir = os.path.join(args.out, docs_dir)
    else:
        default_dirs = True

    ecs_helpers.make_dirs(out_dir)
    ecs_helpers.make_dirs(docs_dir)

    # To debug issues in the gradual building up of the nested structure, insert
    # statements like this after any step of interest.
    # ecs_helpers.yaml_dump('ecs.yml', fields)

    fields = loader.load_schemas(ref=args.ref, included_files=args.include)
    cleaner.clean(fields, strict=args.strict)
    finalizer.finalize(fields)
    fields = subset_filter.filter(fields, args.subset, out_dir)
    nested, flat = intermediate_files.generate(fields, os.path.join(out_dir, 'ecs'), default_dirs)

    if args.intermediate_only:
        exit()

    csv_generator.generate(flat, ecs_version, out_dir)
    es_template.generate(flat, ecs_version, out_dir, args.template_settings, args.mapping_settings)
    beats.generate(nested, ecs_version, out_dir)
    if args.include or args.subset:
        exit()

    asciidoc_fields.generate(nested, ecs_version, docs_dir)