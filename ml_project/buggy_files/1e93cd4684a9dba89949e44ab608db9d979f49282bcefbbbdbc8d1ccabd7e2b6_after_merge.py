def get_web_screenshots(target, scan_id, proctimeout):
    scan_dir = utils.get_scan_dir(scan_id)
    xml_file = os.path.join(scan_dir, f"nmap.{scan_id}.xml")
    output_dir = os.path.join(scan_dir, f"aquatone.{scan_id}")
    logger.info(f"Attempting to take screenshots for {target}")

    aquatoneArgs = ["aquatone", "-nmap", "-scan-timeout", "2500", "-out", output_dir]
    with open(xml_file, "r") as f:
        process = subprocess.Popen(
            aquatoneArgs, stdin=f, stdout=subprocess.DEVNULL
        )  # nosec

    try:
        process.communicate(timeout=proctimeout)
        if process.returncode == 0:
            time.sleep(
                0.5
            )  # a small sleep to make sure all file handles are closed so that the agent can read them
    except subprocess.TimeoutExpired:
        logger.warning(f"TIMEOUT: Killing aquatone against {target}")
        process.kill()

    return parse_aquatone_session(output_dir)