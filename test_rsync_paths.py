import os
from os import makedirs
from os.path import dirname, basename

from utz import cd_tmpdir, proc, sh, TmpDir


def read(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()


def write(path: str, content: str | None = None):
    makedirs(dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content or path)


def test_rsync_paths():
    with cd_tmpdir():
        dir1 = 'aa/bb'
        path1 = f'{dir1}/cc.txt'
        path2 = f'{dir1}/dd.txt'
        path3 = 'aa/bb.txt'
        for path in [path1, path2, path3]:
            write(path)
            write(f'sub/dir/{path}')

        with cd_tmpdir(dir='tmp'):
            sh(f'rsync-paths {path1} ../../ ./')
            files = proc.lines('find . -type f')
            assert files == [f'./{path1}']
            assert read(path1) == path1

        with cd_tmpdir(dir='tmp'):
            sh(f'rsync-paths {dir1} ../../ ./')
            files = proc.lines('find . -type f')
            assert files == [f'./{path1}', f'./{path2}']
            assert read(path1) == path1
            assert read(path2) == path2

        with TmpDir(dir='tmp') as td:
            dst = os.path.join('tmp', basename(td))
            sh(f'rsync-paths {path1} ./ {dst}/')
            files = proc.lines(f'find {dst}/ -type f')
            file = f'{dst}/{path1}'
            assert files == [file]
            assert read(path1) == path1

        with TmpDir(dir='tmp') as td:
            dst = os.path.join('tmp', basename(td))
            sh(f'rsync-paths {dir1} ./ {dst}/')
            files = proc.lines(f'find {dst}/ -type f')
            dst1 = f'{dst}/{path1}'
            dst2 = f'{dst}/{path2}'
            assert files == [dst1, dst2]
            assert read(dst1) == path1
            assert read(dst2) == path2
