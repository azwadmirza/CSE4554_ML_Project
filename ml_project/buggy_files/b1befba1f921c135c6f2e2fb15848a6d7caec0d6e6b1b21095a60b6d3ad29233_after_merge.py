def get_vnc_screenshots(target, scan_id, proctimeout):

    scan_dir = utils.get_scan_dir(scan_id)
    output_file = os.path.join(scan_dir, f"vncsnapshot.{scan_id}.jpg")

    logger.info(f"Attempting to take VNC screenshot for {target}")

    vncsnapshot_args = [
        "xvfb-run",
        "vncsnapshot",
        "-quality",
        "50",
        target,
        output_file,
    ]

    process = subprocess.Popen(
        vncsnapshot_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )  # nosec
    try:
        process.communicate(timeout=proctimeout)
    except subprocess.TimeoutExpired:
        logger.warning(f"TIMEOUT: Killing vncsnapshot against {target}")
        process.kill()

    if not is_valid_image(output_file):
        return {}

    logger.info(f"VNC screenshot acquired for {target} on port 5900")
    return {
        "host": target,
        "port": 5900,
        "service": "VNC",
        "data": base64_file(output_file),
    }