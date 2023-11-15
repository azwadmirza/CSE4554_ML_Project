def scan(target_data, config):

    if not utils.validate_target(target_data["target"], config):
        return False

    target = target_data["target"]
    scan_id = target_data["scan_id"]

    agentConfig = target_data["agent_config"]

    command = command_builder(scan_id, agentConfig, target)
    scan_dir = utils.get_scan_dir(scan_id)

    result = ScanResult(target_data, config)

    try:
        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=int(agentConfig["scanTimeout"]),
        )  # nosec
    except subprocess.TimeoutExpired:
        result.add_item("timed_out", True)
        logger.warning(f"TIMEOUT: Nmap against {target} ({scan_id})")
        return result

    logger.info(f"Nmap {target} ({scan_id}) complete")

    for ext in "nmap", "gnmap", "xml":
        path = os.path.join(scan_dir, f"nmap.{scan_id}.{ext}")
        try:
            with open(path, "r") as f:
                result.add_item(ext + "_data", f.read())
        except Exception:
            logger.warning(f"Couldn't read {path}")
            return False

    try:
        nmap_report = NmapParser.parse(result.result["xml_data"])
    except NmapParserException:
        logger.warning(f"Couldn't parse nmap.{scan_id}.xml")
        return False

    if nmap_report.hosts_total < 1:
        logger.warning(f"No hosts found in nmap.{scan_id}.xml")
        return False
    elif nmap_report.hosts_total > 1:
        logger.warning(f"Too many hosts found in nmap.{scan_id}.xml")
        return False
    elif nmap_report.hosts_down == 1:
        # host is down
        result.is_up(False)
        return result
    elif nmap_report.hosts_up == 1 and len(nmap_report.hosts) == 0:
        # host is up but no reportable ports were found
        result.is_up(True)
        result.add_item("port_count", 0)
        return result
    else:
        # host is up and reportable ports were found
        result.is_up(nmap_report.hosts[0].is_up())
        result.add_item("port_count", len(nmap_report.hosts[0].get_ports()))

    if agentConfig["webScreenshots"] and shutil.which("aquatone") is not None:
        screens = screenshots.get_web_screenshots(
            target, scan_id, agentConfig["webScreenshotTimeout"]
        )
        for item in screens:
            result.add_screenshot(item)

    if (
        agentConfig["vncScreenshots"]
        and "5900/tcp" in result.result["nmap_data"]
        and screenshots.get_vnc_screenshots(
            target, scan_id, agentConfig["vncScreenshotTimeout"]
        )
    ):

        screenshotPath = os.path.join(scan_dir, f"vncsnapshot.{scan_id}.jpg")
        if os.path.isfile(screenshotPath):
            result.add_screenshot(
                {
                    "host": target,
                    "port": 5900,
                    "service": "VNC",
                    "data": screenshots.base64_image(screenshotPath),
                }
            )
            logger.info(f"VNC screenshot acquired for {result.result['ip']}")

    # submit result

    return result