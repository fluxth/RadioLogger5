from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from common.models import Base, Station, Track, Play, ErrorLog

import os.path


class Database(object):

    _THREAD = None

    _config: dict = {}
    _engine = None

    _makeSession = None

    def __init__(self, config):
        self._config = config

    def initialize(self):
        uri: str = self._config['uri'] #self.processDbUri(self._config['uri'])

        self._engine = create_engine(uri) #, echo=True)
        self._makeSession = sessionmaker(bind=self._engine)

        Base.metadata.create_all(self._engine)

    def processDbUri(self, uri):

        # replace relative sqlite uri with absolute
        if 'sqlite:///' in uri:
            start: int = uri.find(':///') + 4
            end: int = None if uri.find('?') < 0 else uri.find('?')

            dbpath: str = uri[start:end]
            base: str = self._THREAD._MASTER.BASE_DIR

            result = uri[:start] + os.path.join(base, dbpath)
            if end is not None:
                result += uri[end:]

            return result

        return uri

    def registerStation(self, station):
        with self.session_scope() as sess:
            st = sess.query(Station).filter_by(name=station._NAME).first()

            if st is None:
                self._THREAD.info('Registering new station: {}'.format(station._NAME))

                st = Station(name=station._NAME)
                default_track = Track(
                    title='[Default Track]',
                    artist=station._NAME,
                    is_default=True,
                    station=st
                )

                sess.add(st)
                sess.add(default_track)

    def logPlay(self, station, metadata):
        with self.session_scope() as sess:
            # get station
            st = sess.query(Station).filter_by(name=station._NAME).first()
        
            # get/create track
            if metadata.isDefault is True:
                track = sess.query(Track).filter_by(is_default=True, station=st).first()
            else:
                track = sess.query(Track).filter_by(
                    title=metadata.title,
                    artist=metadata.artist,
                    station=st,
                    # extra data?
                ).first()

                if track is None:
                    track = Track(
                        title=metadata.title,
                        artist=metadata.artist,
                        station=st,
                        # extra data?
                    )

                    sess.add(track)

                    self._THREAD.info('New Track for {}: {} - {}'.format(
                        station._SHORTNAME,
                        metadata.artist,
                        metadata.title
                    ))

            # check for recurrence then log play
            last_play = sess.query(Play)\
                        .filter(Play.track.has(station=st))\
                        .order_by(Play.id.desc())\
                        .first()

            if last_play is None or last_play.track is not track:
                play = Play(
                    track=track,
                    ts=metadata.timestamp,
                    # extra data?
                )

                sess.add(play)

    def logError(self, station, sender_name, message, details=None):
        with self.session_scope() as sess:
            if station is None:
                db_station = None
            else:
                db_station = sess.query(Station).filter_by(name=station._NAME).first()

            el = ErrorLog(
                station=db_station,
                owner=sender_name,
                message=message,
                details=details
            )

            sess.add(el)

    @contextmanager
    def session_scope(self):
        session = self._makeSession()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def shutdown(self):
        pass
        