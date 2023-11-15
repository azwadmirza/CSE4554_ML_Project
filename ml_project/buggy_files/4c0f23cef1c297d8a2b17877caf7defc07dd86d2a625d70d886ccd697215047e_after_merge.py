def update_messager():
    if not check("TikTokApi"):
        # Outdated
        print("TikTokApi package is outdated, please consider upgrading! \n(You can suppress this by setting ignore_version=True in the TikTokApi constructor)")

    if not check_future_deprecation():
        print("Your version of python is going to be deprecated, for future updates upgrade to 3.7+")