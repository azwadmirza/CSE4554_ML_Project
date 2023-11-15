def format_channel_name(author, guild, exclude_channel=None):
    """Sanitises a username for use with text channel names"""
    name = author.name.lower()
    name = new_name = (
        "".join(l for l in name if l not in string.punctuation and l.isprintable()) or "null"
    ) + f"-{author.discriminator}"

    counter = 1
    existed = set(c.name for c in guild.text_channels if c != exclude_channel)
    while new_name in existed:
        new_name = f"{name}_{counter}"  # multiple channels with same name
        counter += 1

    return new_name