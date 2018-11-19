class BaseAction(object):
	method: str = None
	args: list = []
	kwargs: dict = {}

	def __repr__(self):
		return '<{} m={}, a={}, k={}>'.format(
			self.__class__.__name__, 
			self.method,
			self.args,
			self.kwargs,
		)

class DatabaseAction(BaseAction):
	pass