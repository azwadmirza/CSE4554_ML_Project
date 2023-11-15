def start_objstore(node_ip_address, redis_address,
                   object_manager_port=None, store_stdout_file=None,
                   store_stderr_file=None, manager_stdout_file=None,
                   manager_stderr_file=None, cleanup=True,
                   objstore_memory=None):
    """This method starts an object store process.

    Args:
        node_ip_address (str): The IP address of the node running the object
            store.
        redis_address (str): The address of the Redis instance to connect to.
        object_manager_port (int): The port to use for the object manager. If
            this is not provided, one will be generated randomly.
        store_stdout_file: A file handle opened for writing to redirect stdout
            to. If no redirection should happen, then this should be None.
        store_stderr_file: A file handle opened for writing to redirect stderr
            to. If no redirection should happen, then this should be None.
        manager_stdout_file: A file handle opened for writing to redirect
            stdout to. If no redirection should happen, then this should be
            None.
        manager_stderr_file: A file handle opened for writing to redirect
            stderr to. If no redirection should happen, then this should be
            None.
        cleanup (bool): True if using Ray in local mode. If cleanup is true,
            then this process will be killed by serices.cleanup() when the
            Python process that imported services exits.
        objstore_memory: The amount of memory (in bytes) to start the object
            store with.

    Return:
        A tuple of the Plasma store socket name, the Plasma manager socket
            name, and the plasma manager port.
    """
    if objstore_memory is None:
        # Compute a fraction of the system memory for the Plasma store to use.
        system_memory = psutil.virtual_memory().total
        if sys.platform == "linux" or sys.platform == "linux2":
            # On linux we use /dev/shm, its size is half the size of the
            # physical memory. To not overflow it, we set the plasma memory
            # limit to 0.4 times the size of the physical memory.
            objstore_memory = int(system_memory * 0.4)
            # Compare the requested memory size to the memory available in
            # /dev/shm.
            shm_fd = os.open("/dev/shm", os.O_RDONLY)
            try:
                shm_fs_stats = os.fstatvfs(shm_fd)
                # The value shm_fs_stats.f_bsize is the block size and the
                # value shm_fs_stats.f_bavail is the number of available
                # blocks.
                shm_avail = shm_fs_stats.f_bsize * shm_fs_stats.f_bavail
                if objstore_memory > shm_avail:
                    print("Warning: Reducing object store memory because "
                          "/dev/shm has only {} bytes available. You may be "
                          "able to free up space by deleting files in "
                          "/dev/shm. If you are inside a Docker container, "
                          "you may need to pass an argument with the flag "
                          "'--shm-size' to 'docker run'.".format(shm_avail))
                    objstore_memory = int(shm_avail * 0.8)
            finally:
                os.close(shm_fd)
        else:
            objstore_memory = int(system_memory * 0.8)
    # Start the Plasma store.
    plasma_store_name, p1 = ray.plasma.start_plasma_store(
        plasma_store_memory=objstore_memory,
        use_profiler=RUN_PLASMA_STORE_PROFILER,
        stdout_file=store_stdout_file,
        stderr_file=store_stderr_file)
    # Start the plasma manager.
    if object_manager_port is not None:
        (plasma_manager_name, p2,
         plasma_manager_port) = ray.plasma.start_plasma_manager(
            plasma_store_name,
            redis_address,
            plasma_manager_port=object_manager_port,
            node_ip_address=node_ip_address,
            num_retries=1,
            run_profiler=RUN_PLASMA_MANAGER_PROFILER,
            stdout_file=manager_stdout_file,
            stderr_file=manager_stderr_file)
        assert plasma_manager_port == object_manager_port
    else:
        (plasma_manager_name, p2,
         plasma_manager_port) = ray.plasma.start_plasma_manager(
            plasma_store_name,
            redis_address,
            node_ip_address=node_ip_address,
            run_profiler=RUN_PLASMA_MANAGER_PROFILER,
            stdout_file=manager_stdout_file,
            stderr_file=manager_stderr_file)
    if cleanup:
        all_processes[PROCESS_TYPE_PLASMA_STORE].append(p1)
        all_processes[PROCESS_TYPE_PLASMA_MANAGER].append(p2)
    record_log_files_in_redis(redis_address, node_ip_address,
                              [store_stdout_file, store_stderr_file,
                               manager_stdout_file, manager_stderr_file])

    return ObjectStoreAddress(plasma_store_name, plasma_manager_name,
                              plasma_manager_port)