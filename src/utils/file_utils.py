import errno
import os
import stat


# def remove_read_only(func, path, exc):
#     """Called by shutil.rmtree when it encounters a readonly file.
#
#     :param func:
#     :param path:
#     :param exc:
#     """
#     excvalue = exc[1]
#     if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
#         os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
#         func(path)
#     else:
#         raise RuntimeError('Could not remove {0}'.format(path))