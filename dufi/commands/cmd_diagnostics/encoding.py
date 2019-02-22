# [SublimeLinter @python:3]

import codecs
import ctypes
from chardet.universaldetector import UniversalDetector


def get_active_code_page():
    return ctypes.cdll.kernel32.GetACP()


def is_os_cyrillic():
    return get_active_code_page() == 1251


def normalize_encoding(encoding):
    try:
        return codecs.lookup(encoding).name
    except LookupError:
        raise ValueError(encoding)


CYRILLIC_ENCODINGS = ("cp1251", "utf_8", "iso8859_5", "cp866", "cp855", "koi8_r")
CYRILLIC_ENCODINGS = [normalize_encoding(x) for x in CYRILLIC_ENCODINGS]


def cmp_encoding(a, b):
    return normalize_encoding(a) == normalize_encoding(b)


def get_cp_encoding(code_page):
    # https://msdn.microsoft.com/en-us/library/windows/desktop/dd317756(v=vs.85).aspx

    if code_page == 1200:
        return "utf_16_le"
    elif code_page == 1201:
        return "utf_16_be"
    elif code_page == 12000:
        return "utf_32_le"
    elif code_page == 12001:
        return "utf_32_be"
    elif code_page == 65000:
        return "utf_7"
    elif code_page == 65001:
        return "utf_8"
    else:
        return "cp{}".format(code_page)


def detect_encoding(filename, lines_limit=50000, cyrillic=True, **kwargs):
    _detect_encoding = _detect_encoding_general

    if cyrillic:
        _detect_encoding = _detect_encoding_cyrillic

    return _detect_encoding(filename, lines_limit, **kwargs)


def _detect_encoding_general(filename, lines_limit):
    detector = UniversalDetector()
    feeded = 0

    for i, line in enumerate(open(filename, "rb")):
        try:
            line.decode("ascii")
        except UnicodeDecodeError:
            pass
        else:
            if i > 0:
                continue

        detector.feed(line)
        feeded += 1

        if detector.done:
            break

        if lines_limit and i == lines_limit:
            break

    detector.close()
    encoding = detector.result["encoding"]

    if not encoding:
        raise RuntimeError("cannot detect file encoding")

    try:
        return normalize_encoding(encoding)
    except ValueError:
        raise RuntimeError("cannot detect file encoding")


def _detect_encoding_cyrillic(filename, lines_limit, elasticity=3):
    fp = open(filename, "rb")

    try:
        return _do_detect_encoding_cyrillic(iter(fp), lines_limit, elasticity)
    finally:
        fp.close()


def _do_detect_encoding_cyrillic(it, limit, elasticity):
    lines = []
    count = 0

    cnt, eof = _read_lines(it, lines, limit)
    count += cnt

    while not lines and (count / limit < elasticity):
        cnt, eof = _read_lines(it, lines, limit)
        count += cnt

        if eof:
            break

    if not lines:
        return "cp1251"

    if lines[0].startswith(codecs.BOM_UTF8):
        return "utf_8_sig"

    detector_encoding = _get_detector_encoding(lines)

    if detector_encoding:
        if detector_encoding.startswith("utf_16") \
                or detector_encoding.startswith("utf_32") \
                or cmp_encoding(detector_encoding, "utf_8_sig"):
            return detector_encoding

    encodings = {x: True for x in CYRILLIC_ENCODINGS}

    while True:
        valid = 0

        for encoding, status in encodings.items():
            if not status:
                continue

            if _test_encoding(lines, encoding):
                valid += 1
            else:
                encodings[encoding] = False

        if valid == 0:
            if detector_encoding:
                return detector_encoding

            raise ValueError("cannot detect encoding")

        if valid == 1:
            for encoding, status in encodings.items():
                if status:
                    return encoding

        if eof:
            break

        if count / limit >= elasticity:
            break

        cnt, eof = _read_lines(it, lines, limit)
        count += cnt

    detector_encoding = _get_detector_encoding(lines, encodings)

    if detector_encoding:
        return detector_encoding

    for encoding in CYRILLIC_ENCODINGS:
        if encodings.get(encoding, False):
            if not encoding.startswith("utf"):
                return encoding

    for encoding in CYRILLIC_ENCODINGS:
        if encodings.get(encoding, False):
            return encoding

    raise ValueError("cannot detect encoding")


def _read_lines(it, lines, limit):
    count = 0
    eof = True

    for i, line in enumerate(it):
        try:
            line.decode("ascii")
        except UnicodeDecodeError:
            lines.append(line)
        else:
            if i == 0:
                lines.append(line)

        count += 1

        if i == limit:
            eof = False
            break

    return count, eof


def _test_encoding(lines, encoding):
    for line in lines:
        try:
            line.decode(encoding)
        except UnicodeDecodeError:
            return False

    return True


def _get_detector_encoding(lines, encodings=None):
    detector = UniversalDetector()

    for line in lines:
        detector.feed(line)

        best_encoding = None
        best_confindence = 0

        for enc, conf in _get_detector_result(detector):
            if encodings:
                for _enc, status in encodings.items():
                    if status and _enc == enc:
                        if conf > best_confindence:
                            best_encoding = enc
                            best_confindence = conf
            else:
                if conf > best_confindence:
                    best_encoding = enc
                    best_confindence = conf

        if best_confindence > 0.70:
            detector.close()

            try:
                return normalize_encoding(best_encoding)
            except ValueError:
                raise RuntimeError("cannot detect file encoding")

    return None


def _get_detector_result(detector):
    result = []

    def _f(result, prober):
        try:
            probers = prober.probers
        except AttributeError:
            try:
                encoding = normalize_encoding(prober.charset_name)
            except ValueError:
                pass
            else:
                result.append((encoding, prober.get_confidence()))
        else:
            for x in probers:
                _f(result, x)

    for prober in detector._charset_probers:
        _f(result, prober)

    return result
