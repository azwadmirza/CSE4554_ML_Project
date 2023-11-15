	def copy(self):
		# By using serialization we are absolutely sure all refs are new
		xml = self.tostring()
		try:
			return ParseTree().fromstring(xml)
		except:
			print(">>>", xml, "<<<")
			raise