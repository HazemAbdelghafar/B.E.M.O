from datetime import datetime
from colory.color import Color
import webcolors

allowed_hex_colors = [
    "000000",
    "434343",
    "666666",
    "999999",
    "cccccc",
    "efefef",
    "f3f3f3",
    "ffffff",
    "fb4c2f",
    "ffad47",
    "fad165",
    "16a766",
    "43d692",
    "4a86e8",
    "a479e2",
    "f691b3",
    "f6c5be",
    "ffe6c7",
    "fef1d1",
    "b9e4d0",
    "c6f3de",
    "c9daf8",
    "e4d7f5",
    "fcdee8",
    "efa093",
    "ffd6a2",
    "fce8b3",
    "89d3b2",
    "a0eac9",
    "a4c2f4",
    "d0bcf1",
    "fbc8d9",
    "e66550",
    "ffbc6b",
    "fcda83",
    "44b984",
    "68dfa9",
    "6d9eeb",
    "b694e8",
    "f7a7c0",
    "cc3a21",
    "eaa041",
    "f2c960",
    "149e60",
    "3dc789",
    "3c78d8",
    "8e63ce",
    "e07798",
    "ac2b16",
    "cf8933",
    "d5ae49",
    "0b804b",
    "2a9c68",
    "285bac",
    "653e9b",
    "b65775",
    "822111",
    "a46a21",
    "aa8831",
    "076239",
    "1a764d",
    "1c4587",
    "41236d",
    "83334c",
    "464646",
    "e7e7e7",
    "0d3472",
    "b6cff5",
    "0d3b44",
    "98d7e4",
    "3d188e",
    "e3d7ff",
    "711a36",
    "fbd3e0",
    "8a1c0a",
    "f2b2a8",
    "7a2e0b",
    "ffc8af",
    "7a4706",
    "ffdeb5",
    "594c05",
    "fbe983",
    "684e07",
    "fdedc1",
    "0b4f30",
    "b3efd3",
    "04502e",
    "a2dcc1",
    "c2c2c2",
    "4986e7",
    "2da2bb",
    "b99aff",
    "994a64",
    "f691b2",
    "ff7537",
    "ffad46",
    "662e37",
    "ebdbde",
    "cca6ac",
    "094228",
    "42d692",
    "16a765",
]

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


def hex_to_color_name(hex: str) -> str:
    return Color(hex).name


def color_name_to_hex(color_name: str) -> str:
    hex_color = webcolors.name_to_hex(color_name)

    hex_color = hex_color.lstrip("#")

    closest_color = min(
        allowed_hex_colors,
        key=lambda color: sum(
            (int(color[i : i + 2], 16) - int(hex_color[i : i + 2], 16)) ** 2
            for i in (0, 2, 4)
        ),
    )

    closest_color = "#" + closest_color

    return closest_color


if __name__ == "__main__":
    print(date_to_RFC3339(2022, 1, 1, 0, 0, 0))
    print(RFC3339_to_datetime("2022-01-01T00:00:00.00Z"))
    print(datetime_to_RFC3339(datetime(2022, 1, 1, 0, 0, 0)))
    print(RFC3339_to_date("2022-01-01T00:00:00.00Z"))
    print(epoch_to_datetime(1640995200))
    print(datetime_to_epoch(datetime(2022, 1, 1, 0, 0, 0)))
    print(epoch_to_date(1640995200))
    print(date_to_epoch(2022, 1, 1, 0, 0, 0))
    print(hex_to_color_name("#FF0000"))
    print(color_name_to_hex("red"))
