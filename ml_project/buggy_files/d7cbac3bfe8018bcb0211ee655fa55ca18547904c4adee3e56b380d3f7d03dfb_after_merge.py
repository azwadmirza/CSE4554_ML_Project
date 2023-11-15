def process_screenshots(screenshots: list) -> tuple:
    processed_screenshots = []
    for item in screenshots:
        screenshot = process_screenshot(item)
        if not screenshot:
            current_app.logger.warning(
                f"Received invalid image for {screenshot['hostname']} port {screenshot['port']}"
            )
            continue
        processed_screenshots.append(item)

    return processed_screenshots, len(processed_screenshots)