"""Seekable file object over HTTP range requests, so a huge remote zip can be
listed and partially extracted without downloading it whole."""
import io
import time
import zipfile

import requests


class RangeFile(io.RawIOBase):
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        r = self.session.get(url, headers={"Range": "bytes=0-0"}, timeout=60)
        r.raise_for_status()
        self.size = int(r.headers["Content-Range"].split("/")[1])
        self.pos = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = {0: offset, 1: self.pos + offset, 2: self.size + offset}[whence]
        return self.pos

    def read(self, n=-1):
        if n < 0:
            n = self.size - self.pos
        if n == 0 or self.pos >= self.size:
            return b""
        end = min(self.pos + n, self.size) - 1
        for attempt in range(8):
            try:
                r = self.session.get(
                    self.url, headers={"Range": f"bytes={self.pos}-{end}"}, timeout=120
                )
                if r.status_code == 429:  # Zenodo rate limit: honour Retry-After
                    time.sleep(min(float(r.headers.get("Retry-After", 5)) + attempt * 5, 90))
                    continue
                r.raise_for_status()
                break
            except requests.RequestException:
                if attempt == 7:
                    raise
                time.sleep(2 ** attempt)
        else:
            raise RuntimeError("rate-limited too long: " + self.url)
        self.pos += len(r.content)
        return r.content

    def readinto(self, b):
        data = self.read(len(b))
        b[: len(data)] = data
        return len(data)


def open_remote_zip(url: str) -> zipfile.ZipFile:
    return zipfile.ZipFile(RangeFile(url))
