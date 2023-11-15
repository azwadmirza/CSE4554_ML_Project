    def __init__(self, fname, logger):
        self.logger = logger
        self.excluding = []
        self.noncode = set()
        self.uncovered = set()
        self.uncovered_exceptional = set()
        self.covered = dict()
        self.branches = dict()
        # self.first_record = True
        self.fname = fname
        self.lineno = 0
        self.last_code_line = ""
        self.last_code_lineno = 0
        self.last_code_line_excluded = False
        self.unrecognized_lines = []
        self.deferred_exceptions = []
        self.last_was_specialization_section_marker = False