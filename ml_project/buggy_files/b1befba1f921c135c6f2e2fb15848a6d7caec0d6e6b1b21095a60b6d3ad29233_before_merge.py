def get_vnc_screenshots(target, scan_id, proctimeout):

    scan_dir = utils.get_scan_dir(scan_id)
    outFile = os.path.join(scan_dir, f"vncsnapshot.{scan_id}.jpg")

    logger.info(f"Attempting to take VNC screenshot for {target}")

    process = subprocess.Popen(
        ["xvfb-run", "vncsnapshot", "-quality", "50", target, outFile],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )  # nosec
    try:
        process.communicate(timeout=proctimeout)
        if process.returncode == 0:
            return True
    except Exception:
        try:
            logger.warning(f"TIMEOUT: Killing vncsnapshot against {target}")
            process.kill()
            return False
        except Exception:
            pass

    return False