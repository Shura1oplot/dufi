# [SublimeLinter @python:3]

import datetime


_combine = datetime.datetime.combine


def get_working_time(date_from, date_to,
                     workdays={1: None, 2: None, 3: None, 4: None, 5: None},
                     default_schedule=((datetime.time(9, 0),  datetime.time(12, 0)),
                                       (datetime.time(13, 0), datetime.time(18, 0))),
                     holidays=None,
                     half_holidays=None,
                     custom_schedule=None):
    workdays = {k: v if v else default_schedule for k, v in workdays.items()}
    custom_schedule = custom_schedule or {}
    half_holidays = half_holidays or ()

    holidays_time = []

    for x in sorted(holidays or ()):
        x = _combine(x, datetime.time())
        holidays_time.append((x, x + datetime.timedelta(days=1)))

    delta0 = datetime.timedelta()
    delta1 = datetime.timedelta(days=1)

    cursor = date_from
    cum_delta = datetime.timedelta()

    def next_day(dt):
        return dt.replace(hour=0, minute=0, second=0, microsecond=0) + delta1

    date_to_date = date_to.date()
    max_b = date_to.time()

    def get_next(cursor):
        for (a, b) in holidays_time:
            if a <= cursor < b:
                return b, delta0  # праздники

        d = cursor.date()

        if d in custom_schedule:
            schedule = custom_schedule[d]
        else:
            schedule = workdays.get(cursor.isoweekday())

        if not schedule:
            return next_day(cursor), delta0  # выходной

        t = cursor.time()
        n = None  # ближайщее рабочее время, если курсор вне диапазона рабочего времени
        limit_b = d == date_to_date  # в последнем дне диапазона расчета учитываем время
        is_half_holiday = d in half_holidays
        end_of_day = max(b for _, b in schedule)

        for a, b in schedule:
            if is_half_holiday and b == end_of_day:
                assert b >= datetime.time(1)

                b = b.replace(hour=b.hour - 1)

                if a == b:
                    continue

                assert b > a

            if limit_b:
                if a > max_b:
                    break

                if b > max_b:
                    b = max_b

            if a <= t < b:
                return _combine(d, b), _combine(d, b) - _combine(d, t)  # рабочее время

            if not n and a >= t:
                n = a

        if n is None:  # после окончания рабочего дня
            return next_day(cursor), delta0

        return _combine(d, n), delta0  # до следующего диапазона рабочего времени

    while cursor < date_to:
        new_cursor, delta = get_next(cursor)
        new_cursor = min(new_cursor, date_to)

        # print(cursor, "->", new_cursor, ":", delta)
        assert new_cursor > cursor

        cursor = new_cursor
        cum_delta += delta

    return cum_delta


if __name__ == "__main__":
    print(get_working_time(datetime.datetime(2017, 10, 6, 10),
                           datetime.datetime(2017, 10, 10, 12, 30)))
