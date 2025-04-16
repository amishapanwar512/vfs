from fuse import FUSE, FuseOSError, Operations
import os, sys, errno, time, stat
from collections import defaultdict

class MemoryVFS(Operations):
    def __init__(self):
        self.files = {}
        self.data = {}
        self.fd = 0
        self.links = defaultdict(list)
        now = time.time()
        self.files['/'] = dict(
            st_mode=(stat.S_IFDIR | 0o755),
            st_nlink=2,
            st_size=0,
            st_ctime=now,
            st_mtime=now,
            st_atime=now
        )

    def getattr(self, path, fh=None):
        if path not in self.files:
            raise FuseOSError(errno.ENOENT)
        return self.files[path]

    def readdir(self, path, fh):
        return ['.', '..'] + [name[1:] for name in self.files if name != '/' and os.path.dirname(name) == path]

    def mkdir(self, path, mode):
        now = time.time()
        self.files[path] = dict(
            st_mode=(stat.S_IFDIR | mode),
            st_nlink=2,
            st_size=0,
            st_ctime=now,
            st_mtime=now,
            st_atime=now
        )
        self.files[os.path.dirname(path)]['st_nlink'] += 1

    def rmdir(self, path):
        entries = [p for p in self.files if os.path.dirname(p) == path]
        if entries:
            raise FuseOSError(errno.ENOTEMPTY)
        self.files.pop(path)
        self.files[os.path.dirname(path)]['st_nlink'] -= 1

    def create(self, path, mode):
        now = time.time()
        self.files[path] = dict(
            st_mode=(stat.S_IFREG | mode),
            st_nlink=1,
            st_size=0,
            st_ctime=now,
            st_mtime=now,
            st_atime=now
        )
        self.data[path] = b''
        self.fd += 1
        return self.fd

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        return self.data[path][offset:offset + size]

    def write(self, path, data, offset, fh):
        original = self.data.get(path, b'')
        new_data = original[:offset].ljust(offset, b'\x00') + data
        self.data[path] = new_data + original[offset + len(data):]
        self.files[path]['st_size'] = len(self.data[path])
        self.files[path]['st_mtime'] = time.time()
        return len(data)

    def unlink(self, path):
        self.files.pop(path)
        self.data.pop(path, None)

    def rename(self, old, new):
        self.files[new] = self.files.pop(old)
        if old in self.data:
            self.data[new] = self.data.pop(old)

    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def truncate(self, path, length):
        self.data[path] = self.data[path][:length].ljust(length, b'\x00')
        self.files[path]['st_size'] = length

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: {} <mountpoint>'.format(sys.argv[0]))
        sys.exit(1)
    mountpoint = sys.argv[1]
    FUSE(MemoryVFS(), mountpoint, foreground=True)