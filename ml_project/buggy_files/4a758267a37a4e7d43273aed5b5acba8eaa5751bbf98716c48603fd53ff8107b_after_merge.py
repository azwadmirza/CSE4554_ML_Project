    def fine_grained_increment_follow_imports(self, sources: List[BuildSource]) -> List[str]:
        """Like fine_grained_increment, but follow imports."""
        t0 = time.time()

        # TODO: Support file events

        assert self.fine_grained_manager is not None
        fine_grained_manager = self.fine_grained_manager
        graph = fine_grained_manager.graph
        manager = fine_grained_manager.manager

        orig_modules = list(graph.keys())

        self.update_sources(sources)
        changed_paths = self.fswatcher.find_changed()
        manager.search_paths = compute_search_paths(sources, manager.options, manager.data_dir)

        t1 = time.time()
        manager.log("fine-grained increment: find_changed: {:.3f}s".format(t1 - t0))

        seen = {source.module for source in sources}

        # Find changed modules reachable from roots (or in roots) already in graph.
        changed, new_files = self.find_reachable_changed_modules(
            sources, graph, seen, changed_paths
        )
        sources.extend(new_files)

        # Process changes directly reachable from roots.
        messages = fine_grained_manager.update(changed, [])

        # Follow deps from changed modules (still within graph).
        worklist = changed[:]
        while worklist:
            module = worklist.pop()
            if module[0] not in graph:
                continue
            sources2 = self.direct_imports(module, graph)
            # Filter anything already seen before. This prevents
            # infinite looping if there are any self edges. (Self
            # edges are maybe a bug, but...)
            sources2 = [source for source in sources2 if source.module not in seen]
            changed, new_files = self.find_reachable_changed_modules(
                sources2, graph, seen, changed_paths
            )
            self.update_sources(new_files)
            messages = fine_grained_manager.update(changed, [])
            worklist.extend(changed)

        t2 = time.time()

        def refresh_file(module: str, path: str) -> List[str]:
            return fine_grained_manager.update([(module, path)], [])

        for module_id, state in list(graph.items()):
            new_messages = refresh_suppressed_submodules(
                module_id, state.path, fine_grained_manager.deps, graph, self.fscache, refresh_file
            )
            if new_messages is not None:
                messages = new_messages

        t3 = time.time()

        # There may be new files that became available, currently treated as
        # suppressed imports. Process them.
        while True:
            new_unsuppressed = self.find_added_suppressed(graph, seen, manager.search_paths)
            if not new_unsuppressed:
                break
            new_files = [BuildSource(mod[1], mod[0]) for mod in new_unsuppressed]
            sources.extend(new_files)
            self.update_sources(new_files)
            messages = fine_grained_manager.update(new_unsuppressed, [])

            for module_id, path in new_unsuppressed:
                new_messages = refresh_suppressed_submodules(
                    module_id, path,
                    fine_grained_manager.deps,
                    graph,
                    self.fscache,
                    refresh_file
                )
                if new_messages is not None:
                    messages = new_messages

        t4 = time.time()

        # Find all original modules in graph that were not reached -- they are deleted.
        to_delete = []
        for module_id in orig_modules:
            if module_id not in graph:
                continue
            if module_id not in seen:
                module_path = graph[module_id].path
                assert module_path is not None
                to_delete.append((module_id, module_path))
        if to_delete:
            messages = fine_grained_manager.update([], to_delete)

        fix_module_deps(graph)

        self.previous_sources = find_all_sources_in_build(graph)
        self.update_sources(self.previous_sources)

        # Store current file state as side effect
        self.fswatcher.find_changed()

        t5 = time.time()

        manager.log("fine-grained increment: update: {:.3f}s".format(t5 - t1))
        manager.add_stats(
            find_changes_time=t1 - t0,
            fg_update_time=t2 - t1,
            refresh_suppressed_time=t3 - t2,
            find_added_supressed_time=t4 - t3,
            cleanup_time=t5 - t4)

        return messages