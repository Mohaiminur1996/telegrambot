# imghdr.py - Python 3.11 version (for compatibility with PTB)
# Source: CPython License

def what(file, h=None):
    if h is None:
        if hasattr(file, 'read'):
            h = file.read(32)
        else:
            with open(file, 'rb') as f:
                h = f.read(32)

    for name, testfunc in tests:
        res = testfunc(h)
        if res:
            return name
    return None

def test_rgb(h):
    if h[0:1] == b'\x01':
        return 'rgb'

def test_gif(h):
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

def test_png(h):
    if h[:8] == b'\211PNG\r\n\032\n':
        return 'png'

def test_jpeg(h):
    if h[6:10] == b'JFIF' or h[6:10] == b'Exif':
        return 'jpeg'

def test_bmp(h):
    if h[:2] == b'BM':
        return 'bmp'

def test_tiff(h):
    if h[:2] in (b'II', b'MM'):
        return 'tiff'

def test_webp(h):
    if h[:4] == b'RIFF' and h[8:12] == b'WEBP':
        return 'webp'

tests = [
    ('rgb', test_rgb),
    ('gif', test_gif),
    ('png', test_png),
    ('jpeg', test_jpeg),
    ('bmp', test_bmp),
    ('tiff', test_tiff),
    ('webp', test_webp),
]
