def _migrate_create_metadata(cache, out):
    out.warn("Migration: Generating missing metadata files")
    refs = _get_refs(cache)

    for ref in refs:
        try:
            base_folder = os.path.normpath(os.path.join(cache.store, ref.dir_repr()))
            # Force using a package cache layout for everything, we want to alter the cache,
            # not the editables
            layout = PackageCacheLayout(base_folder=base_folder, ref=ref, short_paths=False,
                                        no_lock=True)
            folder = layout.export()
            try:
                manifest = FileTreeManifest.load(folder)
                rrev = manifest.summary_hash
            except:
                rrev = DEFAULT_REVISION_V1
            metadata_path = os.path.join(layout.conan(), PACKAGE_METADATA)
            if not os.path.exists(metadata_path):
                out.info("Creating {} for {}".format(PACKAGE_METADATA, ref))
                prefs = _get_prefs(layout)
                metadata = PackageMetadata()
                metadata.recipe.revision = rrev
                for pref in prefs:
                    try:
                        pmanifest = FileTreeManifest.load(layout.package(pref))
                        prev = pmanifest.summary_hash
                    except:
                        prev = DEFAULT_REVISION_V1
                    metadata.packages[pref.id].revision = prev
                    metadata.packages[pref.id].recipe_revision = metadata.recipe.revision
                save(metadata_path, metadata.dumps())
        except Exception as e:
            raise ConanException("Something went wrong while generating the metadata.json files "
                                 "in the cache, please try to fix the issue or wipe the cache: {}"
                                 ":{}".format(ref, e))
    out.success("Migration: Generating missing metadata files finished OK!\n")