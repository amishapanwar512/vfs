# Python Virtual File System (VFS) using FUSE

This project implements a fully functional in-memory file system in Linux using Python and FUSE.

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Create mount point:
   mkdir mount

3. Run the filesystem:
   sudo python3 vfs.py mount

4. Test:
   cd mount
   touch test.txt
   echo "Hello" > test.txt
   cat test.txt

5. Unmount:
   fusermount -u mount
