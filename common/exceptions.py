class BaseException(Exception):
	pass

class ConfigurationError(Exception):
	pass

class LoggerBaseException(Exception):
	pass

class StationParseError(LoggerBaseException):
	pass