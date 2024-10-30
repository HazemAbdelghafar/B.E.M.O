from datetime import datetime

# Todo: Implement relative time conversion functions


def date_to_RFC3339(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"


def RFC3339_to_date(date: str) -> tuple:
    return (
        f"{date[:4]}-{date[5:7]}-{date[8:10]} ",
        f"{date[11:13]}:{date[14:16]}:{date[17:19]}",
    )


def RFC3339_to_datetime(date: datetime) -> datetime:
    return datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%S.%fZ")


def datetime_to_RFC3339(date: datetime) -> str:
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def date_to_epoch(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> int:
    return int(datetime(year, month, day, hour, minute, second).timestamp())


def epoch_to_date(epoch: int) -> str:
    return (
        f"{datetime.fromtimestamp(epoch).year}-{datetime.fromtimestamp(epoch).month}-{datetime.fromtimestamp(epoch).day} "
        f"{datetime.fromtimestamp(epoch).hour}:{datetime.fromtimestamp(epoch).minute}:{datetime.fromtimestamp(epoch).second}"
    )


def datetime_to_epoch(date: datetime) -> int:
    return int(date.timestamp())


def epoch_to_datetime(epoch: int) -> datetime:
    return datetime.fromtimestamp(epoch)


if __name__ == "__main__":
    print(date_to_RFC3339(2022, 1, 1, 0, 0, 0))
    print(RFC3339_to_datetime("2022-01-01T00:00:00.00Z"))
    print(datetime_to_RFC3339(datetime(2022, 1, 1, 0, 0, 0)))
    print(RFC3339_to_date("2022-01-01T00:00:00.00Z"))
    print(epoch_to_datetime(1640995200))
    print(datetime_to_epoch(datetime(2022, 1, 1, 0, 0, 0)))
    print(epoch_to_date(1640995200))
    print(date_to_epoch(2022, 1, 1, 0, 0, 0))
