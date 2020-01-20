from stations.SiriusXMBase import SiriusXMBase

class KIISXMStation(SiriusXMBase):
    _NAME = 'KIISXM'
    _SHORTNAME = 'KIS'

    _XMCH = '8241'
    _CUTTYPE = 'Talk'

    def isDefaultMetadata(self, metadata):
        keywords = ['KIIS', 'LAs #1 Hit Music']
        if any(k in metadata.title for k in keywords) or any(k in metadata.artist for k in keywords):
            return None

        return False