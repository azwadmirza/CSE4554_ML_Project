def strings_on_ipa(bin_path):
    """Extract Strings from IPA"""
    try:
        logger.info("Running strings against the Binary")
        unique_str = []
        unique_str = list(set(strings_util(bin_path)))  # Make unique
        unique_str = [escape(ip_str)
                      for ip_str in unique_str]  # Escape evil strings
        return unique_str
    except:
        PrintException("Running strings against the Binary")