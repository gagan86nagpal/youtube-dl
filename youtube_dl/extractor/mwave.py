from __future__ import unicode_literals

from .common import InfoExtractor
from ..compat import compat_str
from ..utils import (
    int_or_none,
    parse_duration,
)


class MwaveIE(InfoExtractor):
    _VALID_URL = r'https?://mwave\.interest\.me/mnettv/videodetail\.m\?searchVideoDetailVO\.clip_id=(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://mwave.interest.me/mnettv/videodetail.m?searchVideoDetailVO.clip_id=168859',
        # md5 is unstable
        'info_dict': {
            'id': '168859',
            'ext': 'flv',
            'title': '[M COUNTDOWN] SISTAR - SHAKE IT',
            'thumbnail': 're:^https?://.*\.jpg$',
            'uploader': 'M COUNTDOWN',
            'duration': 206,
            'view_count': int,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        vod_info = self._download_json(
            'http://mwave.interest.me/onair/vod_info.m?vodtype=CL&sectorid=&endinfo=Y&id=%s' % video_id,
            video_id, 'Download vod JSON')

        formats = []
        for num, cdn_info in enumerate(vod_info['cdn']):
            stream_url = cdn_info.get('url')
            if not stream_url:
                continue
            stream_name = cdn_info.get('name') or compat_str(num)
            f4m_stream = self._download_json(
                stream_url, video_id,
                'Download %s stream JSON' % stream_name)
            f4m_url = f4m_stream.get('fileurl')
            if not f4m_url:
                continue
            formats.extend(
                self._extract_f4m_formats(f4m_url + '&hdcore=3.0.3', video_id, f4m_id=stream_name))
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': vod_info['title'],
            'thumbnail': vod_info.get('cover'),
            'uploader': vod_info.get('program_title'),
            'duration': parse_duration(vod_info.get('time')),
            'view_count': int_or_none(vod_info.get('hit')),
            'formats': formats,
        }
