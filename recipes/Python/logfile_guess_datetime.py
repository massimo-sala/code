"""
This module permits to extract from text files the first string similar to a datetime or date.
Note: the parsing is done as text, so it can catch spurious values.

Example:
	import sys, logfile_guess_datetime
	filename = sys.argv[1]
	guess = logfile_guess_datetime.guess_datetime(365, "Italian")
	print("Localized months:", guess.MONTHS_LOCAL)
	print(guess.from_file_content(filename))


The months in short form (Jan, Feb, etc...) are always searched in English;
to scan files written in another language specify a <locale>.
"""

__AUTHOR__ = "massimo.sala.71@gmail.com"
# license: MIT; please report bugs and improvements writing to me by email

import calendar, datetime, locale, string, time
# locale: https://bugs.python.org/issue10466
# calendar: https://bugs.python.org/issue10092


class guess_datetime :
	"""
	past_days:
		look for dates >= now - past_days
	_locale:
		''			search in English and in the system locale
		<value>		search in English and in the specified locale; value format is, for example, "it_IT" or "Italian"
	"""
	def __init__(self, past_days, _locale) :
		self.SEPS = " -/:"
		self.CHARS = self.SEPS + string.digits + string.ascii_uppercase

		self.epoch_max = time.time()
		self.epoch_min = self.epoch_max - 86400 * past_days
		self.year_max = datetime.datetime.now().year
		self.year_min = (datetime.datetime.now() - datetime.timedelta(days = past_days)).year

		self.MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()
		self.MONTHS_LOCAL = []
		i = None
		try :
			old = locale._setlocale(locale.LC_TIME, _locale)
			i = calendar.month_abbr[1 :]
			locale._setlocale(locale.LC_TIME, old)
		except :
			pass
		if i :
			self.MONTHS_LOCAL = map(str.lower, i)


	def from_file_content(self, filename, time_width = 10 + 1 + 8, header_size = 4096) :
		"""
		2020-04-23 03:10:51
		Apr 25 01:10:15 srv
		apr 28  2020 3:09:2
		audit.log: type=USER_LOGIN msg=audit(1587977971.550:257): user
		apache tomcat: 10.1.1.51 - - [29/Apr/2020:06:50:13 +0200] "GET /fo
		pgbadger: 7a riga: <meta http-equiv="Expires" content="Wed Apr 29 23:55:03 2020">
		"""
		try :
			head = open(filename, 'r').read(header_size)
		except :
			return
		i = head.find('\0')
		if i >= 0 :
			return

		for line in head.split('\n') :
			line = line.lower().strip()
			if line.startswith("date: ") :
				return	line[6 :]

			for i, w in enumerate(self.MONTHS + self.MONTHS_LOCAL) :
				line = line.replace(w, w.upper())

			line = ' '.join(['' if w.count('.') >= 3 else w for w in line.split()])		# skip ipaddr

			line = ''.join(map(lambda c: c if c in self.CHARS else ' ', line)).strip()		# keep digits and MONTHS

			for w in line.split() :
				if w.isdigit() and self.epoch_min < int(w) < self.epoch_max :
					dt = datetime.datetime.fromtimestamp(int(w))
					return	str(dt)

			line = ' '.join(line.split())						# to single space
			while line and line[0] in self.SEPS :
				line = line[1 :]

			nline = []
			for w in line.split() :
				if w.isdigit() :
					if not (1 <= int(w) <= 31) and not (self.year_min <= int(w) <= self.year_max) :
						continue
				nline.append(w)
			line = ' '.join(nline)
			line = line[: time_width]

			i = len(filter(str.isdigit, line))
			if i >= 6 and i < len(line.replace(' ', '')) :
				return	line
