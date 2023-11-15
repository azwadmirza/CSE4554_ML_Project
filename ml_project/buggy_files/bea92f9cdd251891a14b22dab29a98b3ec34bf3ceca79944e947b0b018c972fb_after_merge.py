  def __init__(self, username=None, password=None, nogui=False):
    if nogui:
      self.display = Display(visible=0, size=(800, 600))
      self.display.start()

    chromedriver_location = './assets/chromedriver'
    chrome_options = Options()
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--lang=en-US')
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})
    chrome_options.binary_location = chromedriver_location
    self.browser = webdriver.Chrome(chromedriver_location, chrome_options=chrome_options)
    self.browser.implicitly_wait(25)

    self.logFile = open('./logs/logFile.txt', 'a')
    self.logFile.write('Session started - %s\n' \
                       % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    self.username = username or environ.get('INSTA_USER')
    self.password = password or environ.get('INSTA_PW')
    self.nogui = nogui


    self.do_comment = False
    self.comment_percentage = 0
    self.comments = ['Cool!', 'Nice!', 'Looks good!']
    self.photo_comments = []
    self.video_comments = []

    self.followed = 0
    self.follow_restrict = load_follow_restriction()
    self.follow_times = 1
    self.do_follow = False
    self.follow_percentage = 0
    self.dont_include = []
    self.automatedFollowedPool = []

    self.dont_like = ['sex', 'nsfw']
    self.ignore_if_contains = []
    self.ignore_users = []

    self.use_clarifai = False
    self.clarifai_secret = None
    self.clarifai_id = None
    self.clarifai_img_tags = []
    self.clarifai_full_match = False

    self.like_by_followers_upper_limit = 0
    self.like_by_followers_lower_limit = 0

    self.aborting = False