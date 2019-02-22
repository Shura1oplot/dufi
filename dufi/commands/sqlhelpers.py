# [SublimeLinter @python:3]


def get_sql_name(s):
    if s is None:
        s = ""
    elif not isinstance(s, str):
        s = str(s)

    return "[{}]".format(s.replace("]", "]]"))


def get_sql_str_no_quotes(s):
    if s is None:
        s = ""
    elif not isinstance(s, str):
        s = str(s)

    return s.replace("'", "''")


def get_sql_str(s):
    return "'{}'".format(get_sql_str_no_quotes(s).replace("'", "''"))


def get_sql_name_str(s):
    return get_sql_str(get_sql_name(s))


class _FormatWrapper():

    def __init__(self, value, n=0):
        super().__init__()
        self._value = value
        self._n = n

    @property
    def raw(self):
        return self._value

    @property
    def str(self):
        return self.__class__(get_sql_str(self._value), self._n + 1)

    @property
    def str_nq(self):
        return self.__class__(get_sql_str_no_quotes(self._value), self._n + 1)

    @property
    def int(self):
        return self.__class__(int(self._value), self._n + 1)

    @property
    def name(self):
        return self.__class__(get_sql_name(self._value), self._n + 1)

    @property
    def comment(self):
        return "/*" if self._value else ""

    @property
    def uncomment(self):
        return "" if self._value else "/*"

    @property
    def enum(self):
        return _FormatEnum(self._value)

    def __str__(self):
        if self._n == 0:
            raise ValueError("dangerous substitution usage", self._value)

        return str(self._value)


class _FormatEnum():

    def __init__(self, values):
        super().__init__()
        self._values = values

    def __getattr__(self, name):
        if not self._values:
            return "(NULL)"

        return "({})".format(", ".join(
            str(getattr(_FormatWrapper(x), name)) for x in self._values))

    def __str__(self):
        return self.str


def sqlfmt(*args, **kwargs):
    if not args:
        raise ValueError("template not specified")

    template, *args = args

    return template.format(
        *[_FormatWrapper(x) for x in args],
        **{k: _FormatWrapper(v) for k, v in kwargs.items()})
