# [SublimeLinter @python:3]

import sys
import os
import codecs
import csv


BUFFER_SIZE = 50 * 1024 * 1024


def iconv(from_code,
          to_code,
          inputfile=None,
          output=None,
          separator=None,
          with_qualifier=True,
          add_filename=False,
          drop_first_row=False):
    from_code = from_code.lower().replace("_", "-")
    to_code = to_code.lower().replace("_", "-")

    from_bom = None
    to_bom = None

    enc_bom = {"utf-32":    codecs.BOM_UTF32,
               "utf-32-be": codecs.BOM_UTF32_BE,
               "utf-32-le": codecs.BOM_UTF32_LE,
               "utf-16":    codecs.BOM_UTF16,
               "utf-16-be": codecs.BOM_UTF16_BE,
               "utf-16-le": codecs.BOM_UTF16_LE}

    if from_code.startswith("utf") and from_code.endswith("-sig") \
            and "8" not in from_code:
        from_code = codecs.lookup(from_code[:-4]).name
        from_bom = enc_bom[from_code]

    if to_code.startswith("utf") and to_code.endswith("-sig") \
            and "8" not in to_code:
        to_code = codecs.lookup(to_code[:-4]).name
        to_bom = enc_bom[to_code]

    if inputfile:
        fin = open(inputfile, "rb")
        close_fin = True
    else:
        fin = sys.stdin.buffer.raw
        close_fin = False

    if output:
        fout = open(output, "ab")
        close_fout = True
    else:
        fout = sys.stdout.buffer.raw
        close_fout = False

    if from_bom:
        assert fin.read(len(from_bom)) == from_bom

    if to_bom:
        fout.write(to_bom)

    if separator is None:
        while True:
            data = fin.read(BUFFER_SIZE)

            if not data:
                break

            fout.write(data.decode(from_code, errors="replace")
                           .encode(to_code, errors="replace"))

    else:
        filename = os.path.normpath(inputfile).replace("\t", " ").replace("\n", " ")

        ufin = codecs.getreader(from_code)(fin, errors="replace")
        ufout = codecs.getwriter(to_code)(fout, errors="replace")

        csv_args = {
            "delimiter": bytes([separator]).decode()
        }

        if not with_qualifier:
            csv_args["quoting"] = csv.QUOTE_NONE
            csv_args["escapechar"] = ""
            csv_args["quotechar"] = ""

        it = iter(csv.reader(ufin, **csv_args))

        if drop_first_row:
            next(it)

        for row in it:
            if add_filename:
                ufout.write(filename)
                ufout.write("\t")

            ufout.write("\t".join(
                value.strip().replace("\t", " ").replace("\r", " ").replace("\n", "")
                for value in row))
            ufout.write("\r\n")

        ufout.flush()

    fout.flush()

    if close_fin:
        fin.close()

    if close_fout:
        fout.close()
