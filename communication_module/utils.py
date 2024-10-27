from datetime import datetime


def date_to_RFC3339(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"


def RFC3339_to_datetime(date: datetime) -> datetime:
    try:
        return datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            return datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S.%fZ")
        except ValueError:
            return datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S.%f")


def datetime_to_RFC3339(date: datetime) -> str:
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    print(date_to_RFC3339(2022, 1, 1, 0, 0, 0))
    print(RFC3339_to_datetime("2022-01-01T00:00:00Z"))
    print(datetime_to_RFC3339(datetime(2022, 1, 1, 0, 0, 0)))
