import os, fcntl, tempfile, json
from .LockedOpen import LockedOpen

class DictPersistJSON(dict):

	def __init__(self, filename, *args, **kwargs):
		self.filename = filename
		self._update(*args, **kwargs) # set from args
		self._load() # overwrite loaded items with file items
		self._dump() # save result to file

	def _load(self):
		if os.path.isfile(self.filename) and os.path.getsize(self.filename) > 0:
			with open(self.filename, 'r') as fh:
				self._update(json.load(fh))

	def _dump(self):
		with LockedOpen(self.filename, 'a') as fh:
			with tempfile.NamedTemporaryFile('w', dir=os.path.dirname(self.filename), delete=False) as tf:
				json.dump(self, tf, indent="\t")
				tempname = tf.name

			os.replace(tempname, self.filename)		

	def _update(self, *args, **kwargs):
		# internal update does not trigger dump
		for k, v in dict(*args, **kwargs).items():
			dict.__setitem__(self, k, v)

	def __getitem__(self, key):
		return dict.__getitem__(self, key)

	def __setitem__(self, key, val):
		dict.__setitem__(self, key, val)
		self._dump()

	def __repr__(self):
		dictrepr = dict.__repr__(self)
		return '%s(%s)' % (type(self).__name__, dictrepr)

	def update(self, *args, **kwargs):
		self._update(*args, **kwargs)
		self._dump()

