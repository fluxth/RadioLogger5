from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, Integer as INTEGER

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, LargeBinary, Boolean, ForeignKey

from datetime import datetime, timezone


Base = declarative_base()


class DoubleTimestamp(TypeDecorator):
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
	ts = Column(DoubleTimestamp, default=datetime.utcnow())

	def __str__(self):
		return '<Station {}>'.format(self.name)

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
	ts = Column(DoubleTimestamp, default=datetime.utcnow())

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
	ts = Column(DoubleTimestamp, default=datetime.utcnow())

	def __str__(self):
		return '<Play track={}>'.format(
			self.track
		)
