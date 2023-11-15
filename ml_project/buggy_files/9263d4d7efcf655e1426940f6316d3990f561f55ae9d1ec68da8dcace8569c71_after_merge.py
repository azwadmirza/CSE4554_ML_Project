	def __init__(self, name) :
		"""
		@param name: URL to be opened
		@keyword additional_headers: additional HTTP request headers to be added to the call
		"""
		try :
			# Note the removal of the fragment ID. This is necessary, per the HTTP spec
			req = Request(url=name.split('#')[0])

			req.add_header('Accept', 'text/html, application/xhtml+xml')

			self.data		= urlopen(req)
			self.headers	= self.data.info()

			if URIOpener.CONTENT_LOCATION in self.headers :
				self.location = urljoin(self.data.geturl(),self.headers[URIOpener.CONTENT_LOCATION])
			else :
				self.location = name

		except urllib_HTTPError :
			e = sys.exc_info()[1]
			from pyMicrodata import HTTPError
			msg = BaseHTTPRequestHandler.responses[e.code]
			raise HTTPError('%s' % msg[1], e.code)
		except Exception :
			e = sys.exc_info()[1]
			from pyMicrodata import MicrodataError
			raise MicrodataError('%s' % e)