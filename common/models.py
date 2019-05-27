from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import TypeDecorator, Integer as INTEGER

from sqlalchemy.orm import relationship
from sqlalchemy import (
	Column, 
	Integer, 
	String, 
	Text,
	LargeBinary, 
	Boolean, 
	ForeignKey
)

from datetime import datetime, timezone

from passlib.hash import bcrypt
import msgpack

from common.utils import resolve_dict


Base = declarative_base()


class PaddedTimestamp(TypeDecorator):
    impl = INTEGER
    _PAD = 1262304000 # Jan 1, 2010

    def process_bind_param(self, value, dialect):
        return int(value.replace(tzinfo=timezone.utc).timestamp()) - self._PAD

    def process_result_value(self, value, dialect):
        return datetime.utcfromtimestamp(value + self._PAD)

class Station(Base):
	__tablename__ = 'stations'

	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True, nullable=False)
	tracks = relationship('Track', back_populates='station')
	error_logs = relationship('ErrorLog', back_populates='station')
	ts = Column(PaddedTimestamp, default=datetime.utcnow())

	def __str__(self):
		return '<Station {}>'.format(self.name)

class ErrorLog(Base):
	__tablename__ = 'error_logs'

	id = Column(Integer, primary_key=True)
	station_id = Column(Integer, ForeignKey('stations.id'))
	station = relationship('Station', back_populates='error_logs')
	owner = Column(String, nullable=False)
	message = Column(String, nullable=False)
	details = Column(Text)
	ts = Column(PaddedTimestamp, default=datetime.utcnow())

	def __str__(self):
		return '<ErrorLog station={} owner={} msg={}>'.format(self.station, self.owner, self.message)

class Track(Base):
	__tablename__ = 'tracks'

	id = Column(Integer, primary_key=True)
	title = Column(String)
	artist = Column(String)
	extras = Column(LargeBinary)
	is_default = Column(Boolean, default=False)
	station_id = Column(Integer, ForeignKey('stations.id'), nullable=False)
	station = relationship('Station', back_populates='tracks')
	plays = relationship('Play', back_populates='track')
	ts = Column(PaddedTimestamp, default=datetime.utcnow())

	def get_extra(self, key, raise_error=True):
		try:
			if self.extras is None:
				raise KeyError(key)

			orig = msgpack.unpackb(self.extras, encoding='utf-8')
			#print(orig)
			return resolve_dict(orig, key)
		except KeyError:
			if not raise_error:
				return None
			raise

	def set_extra(self, key, value):
		orig = {}
		if self.extras is not None:
			orig = msgpack.unpackb(self.extras, encoding='utf-8')

		def put(d, keys, item):
			if "." in keys:
				key, rest = keys.split(".", 1)
				if key not in d:
					d[key] = {}
				put(d[key], rest, item)
			else:
				d[keys] = item

		put(orig, key, value)

		self.extras = msgpack.packb(orig, use_bin_type=True)
			
	def merge_extra(self, in_dict):
		pass

	def __str__(self):
		return '<Track title="{}" artist="{}" station={}>'.format(
			self.title,
			self.artist,
			self.station
		)

class Play(Base):
	__tablename__ = 'plays'

	id = Column(Integer, primary_key=True)
	track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False)
	track = relationship('Track', back_populates='plays')
	extras = Column(LargeBinary)
	ts = Column(PaddedTimestamp, default=datetime.utcnow())

	def __str__(self):
		return '<Play track={}>'.format(
			self.track
		)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(15), nullable=False, unique=True)
    email = Column(String(300))
    password = Column(String(300), nullable=False)
    perms = Column(Integer, default=0)

    def __init__(self, username, password, email):
        self.username = username
        self.password = bcrypt.encrypt(password)
        self.email = email

    def validate_password(self, password):
        return bcrypt.verify(password, self.password)

    def __repr__(self):
        return "<User(username ='%s', password='%s', email='%s')>" % (self.username, self.password, self.email)
