from stations.SiriusXMBase import SiriusXMBase

class Z100XMStation(SiriusXMBase):
    _NAME = 'Z100XM'
    _SHORTNAME = 'Z100'

    _XMCH = '8242'
    _CUTTYPE = 'Talk'

    def isDefaultMetadata(self, metadata):
        keywords = ['Z100', 'NYs #1 Hit Music']
        if any(k in metadata.title for k in keywords) or any(k in metadata.artist for k in keywords):
            return None

        return False