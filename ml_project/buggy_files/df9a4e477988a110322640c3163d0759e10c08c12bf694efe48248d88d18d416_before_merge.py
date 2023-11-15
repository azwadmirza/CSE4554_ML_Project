    def __init__(self, game_id=None):
        super().__init__()
        self.id = game_id  # pylint: disable=invalid-name
        self.runner = None
        self.config = None

        # Load attributes from database
        game_data = pga.get_game_by_field(game_id, "id")
        self.slug = game_data.get("slug") or ""
        self.runner_name = game_data.get("runner") or ""
        self.directory = game_data.get("directory") or ""
        self.name = game_data.get("name") or ""

        self.game_config_id = game_data.get("configpath") or ""
        self.is_installed = bool(game_data.get("installed")) and self.game_config_id
        self.platform = game_data.get("platform") or ""
        self.year = game_data.get("year") or ""
        self.lastplayed = game_data.get("lastplayed") or 0
        self.steamid = game_data.get("steamid") or ""
        self.has_custom_banner = bool(game_data.get("has_custom_banner"))
        self.has_custom_icon = bool(game_data.get("has_custom_icon"))
        try:
            self.playtime = float(game_data.get("playtime") or 0.0)
        except ValueError:
            logger.error("Invalid playtime value %s", game_data.get("playtime"))

        if self.game_config_id:
            self.load_config()
        self.game_thread = None
        self.prelaunch_executor = None
        self.heartbeat = None
        self.killswitch = None
        self.state = self.STATE_IDLE
        self.exit_main_loop = False
        self.xboxdrv_thread = None
        self.game_runtime_config = {}
        self.resolution_changed = False
        self.compositor_disabled = False
        self.stop_compositor = self.start_compositor = ""
        self.original_outputs = None
        self.log_buffer = Gtk.TextBuffer()
        self.log_buffer.create_tag("warning", foreground="red")

        self.timer = Timer()