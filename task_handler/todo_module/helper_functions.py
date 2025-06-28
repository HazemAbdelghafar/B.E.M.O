from datetime import datetime
from colory.color import Color
import webcolors
import pytz
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from utilities import UserData

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    filename="./logging.log",
    encoding="utf-8",
    level=logging.DEBUG,
)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

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

allowed_timezones = [tz_ for tz_ in pytz.all_timezones]

# Time Conversion Functions
## Supported Formats: RFC3339, Datetime, Date and Time, Epoch, Relative Time


def get_current_time(timezone: str = "UTC") -> datetime:
    """
    Get the current time in the specified timezone.

    Args:
        timezone (str, optional): The timezone to get the current time in. Defaults to "UTC".

    Returns:
        datetime: The current time in the specified timezone.
    """
    if timezone not in allowed_timezones:
        logger.error("Invalid timezone, Defaulting to UTC")
        timezone = "UTC"

    return datetime.now(pytz.timezone(timezone))


## RFC3339
########################################################################################
def RFC3339_to_date_and_time(date: str) -> tuple:
    """
    Converts an RFC3339 formatted date string to separate date and time strings.

    Args:
        date (str): The RFC3339 formatted date string.

    Returns:
        tuple: A tuple containing the date and time strings in the format (date, time) if the conversion is successful, otherwise a tuple containing ("Invalid Date", "Invalid Time").
    """
    try:
        return (
            f"{date[:4]}-{date[5:7]}-{date[8:10]} ",
            f"{date[11:13]}:{date[14:16]}:{date[17:19]}",
        )
    except:
        return ("Invalid Date", "Invalid Time")


def RFC3339_to_datetime(date: datetime) -> datetime:
    """
    Converts a date string in RFC3339 format to a datetime object.

    Args:
        date (datetime): The date string in RFC3339 format.

    Returns:
        datetime: The converted datetime object if the conversion is successful, otherwise the current time.
    """
    try:
        return datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        return datetime.now()


def RFC3339_to_epoch(date: str) -> int:
    """
    Converts a date string in RFC3339 format to epoch timestamp.

    Args:
        date (str): The date string in RFC3339 format ("%Y-%m-%dT%H:%M:%S.%fZ").

    Returns:
        int: The epoch timestamp corresponding to the input date string.
             Returns -1 if the conversion fails.
    """
    try:
        return int(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
    except:
        return -1


def RFC3339_to_relative_time(date: str, timezone: str = "UTC") -> str:
    """
    Converts an RFC3339 formatted date string to a relative time string.

    Args:
        date (str): The RFC3339 formatted date string.
        timezone (str, optional): The timezone to use for the conversion. Defaults to "UTC".

    Returns:
        str: The relative time string if the conversion is successful, otherwise "Invalid Date" or "Invalid Timezone" or "Future Date".
    """
    try:
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        epoch = int(date.timestamp())
    except:
        return "Invalid Date"

    return epoch_to_relative_time(epoch, timezone)


def RFC3339_change_timezones(
    date: str, from_timezone: str = "UTC", to_timezone: str = "UTC"
) -> str:
    """
    Converts an RFC3339 formatted date string from one timezone to another.

    Args:
        date (str): The RFC3339 formatted date string.
        from_timezone (str): The timezone of the input date string.
        to_timezone (str): The timezone to convert the input date string to.

    Returns:
        str: The date string in the new timezone if the conversion is successful, otherwise "Invalid Date" or "Invalid Timezone".
    """
    try:
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        return "Invalid Date"

    if from_timezone not in allowed_timezones:
        logger.error("Invalid timezone, Defaulting to UTC")
        from_timezone = "UTC"

    if to_timezone not in allowed_timezones:
        logger.error("Invalid timezone, Defaulting to UTC")
        to_timezone = "UTC"

    try:
        date = pytz.timezone(from_timezone).localize(date)
        date = date.astimezone(pytz.timezone(to_timezone))
        return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        return "Invalid Timezone"


## Datetime
########################################################################################
def datetime_to_RFC3339(date: datetime) -> str:
    """
    Converts a datetime object to a string in RFC3339 format.

    Args:
        date (datetime): The datetime object to be converted.

    Returns:
        str: The datetime string in RFC3339 format if the conversion is successful, otherwise "Invalid Date".
    """
    try:
        return date.strftime("%Y-%m-%dT%H:%M:%SZ")
    except:
        return "Invalid Date"


def datetime_to_date_and_time(date: datetime) -> tuple:
    """
    Converts a datetime object to a tuple containing the date and time components.

    Args:
        date (datetime): The datetime object to convert.

    Returns:
        tuple: A tuple containing the date and time components in the format (date, time) if the conversion is successful, otherwise a tuple containing ("Invalid Date", "Invalid Time").
    """
    try:
        return (
            f"{date.year}-{date.month}-{date.day} ",
            f"{date.hour}:{date.minute}:{date.second}",
        )
    except:
        return ("Invalid Date", "Invalid Time")


def datetime_to_epoch(date: datetime) -> int:
    """
    Converts a datetime object to epoch timestamp.

    Args:
        date (datetime): The datetime object to be converted.

    Returns:
        int: The epoch timestamp of the given datetime object, returns -1 if the conversion fails.
    """
    try:
        return int(date.timestamp())
    except:
        return -1


def datetime_to_relative_time(date: datetime, timezone: str = "UTC") -> str:
    """
    Converts a datetime object to a relative time string.

    Args:
        date (datetime): The datetime object to convert.
        timezone (str, optional): The timezone to use for the conversion. Defaults to "UTC".

    Returns:
        str: The relative time string representing the datetime object if the conversion is successful, otherwise "Invalid Date" or "Invalid Timezone" or "Future Date".
    """

    return epoch_to_relative_time(date.timestamp(), timezone)


## Date and Time
########################################################################################
def date_and_time_to_RFC3339(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> str:
    """
    Converts the given date and time components to RFC3339 format.

    Args:
        year (int): The year component of the date.
        month (int): The month component of the date.
        day (int): The day component of the date.
        hour (int): The hour component of the time.
        minute (int): The minute component of the time.
        second (int): The second component of the time.

    Returns:
        str: The date and time in RFC3339 format if the conversion is successful, otherwise "Invalid Date".
    """
    if year < 0 or month < 0 or day < 0 or hour < 0 or minute < 0 or second < 0:
        return "Invalid Date"

    if month > 12 or day > 31 or hour > 23 or minute > 59 or second > 59:
        return "Invalid Date"

    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"


def date_and_time_to_epoch(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> int:
    """
    Converts a given date and time to epoch timestamp.

    Args:
        year (int): The year.
        month (int): The month.
        day (int): The day.
        hour (int): The hour.
        minute (int): The minute.
        second (int): The second.

    Returns:
        int: The epoch timestamp if the conversion is successful, otherwise -1.
    """
    if year < 0 or month < 0 or day < 0 or hour < 0 or minute < 0 or second < 0:
        return -1

    if month > 12 or day > 31 or hour > 23 or minute > 59 or second > 59:
        return -1

    return int(datetime(year, month, day, hour, minute, second).timestamp())


def date_and_time_to_datetime(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> datetime:
    """
    Convert the given date and time components into a datetime object.

    Args:
        year (int): The year component of the date.
        month (int): The month component of the date.
        day (int): The day component of the date.
        hour (int): The hour component of the time.
        minute (int): The minute component of the time.
        second (int): The second component of the time.

    Returns:
        datetime: The datetime object representing the given date and time if the conversion is successful, otherwise the current time.
    """
    if year < 0 or month < 0 or day < 0 or hour < 0 or minute < 0 or second < 0:
        return datetime.now()

    if month > 12 or day > 31 or hour > 23 or minute > 59 or second > 59:
        return datetime.now()

    return datetime(year, month, day, hour, minute, second)


def date_and_time_to_relative_time(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    timezone: str = "UTC",
) -> str:
    """
    Converts a given date and time to a relative time string.

    Args:
        year (int): The year of the date.
        month (int): The month of the date.
        day (int): The day of the date.
        hour (int): The hour of the time.
        minute (int): The minute of the time.
        second (int): The second of the time.
        timezone (str, optional): The timezone of the date and time. Defaults to "UTC".

    Returns:
        str: The relative time string representing the time difference between the given date and time and the current time,
        or "Invalid Date" or "Invalid Timezone" or "Future Date" if the date, time, or timezone is invalid.
    """

    if year < 0 or month < 0 or day < 0 or hour < 0 or minute < 0 or second < 0:
        return "Invalid Date"

    if month > 12 or day > 31 or hour > 23 or minute > 59 or second > 59:
        return "Invalid Date"

    if timezone not in allowed_timezones:
        logger.error("Invalid timezone, Defaulting to UTC")
        timezone = "UTC"

    return epoch_to_relative_time(
        datetime(year, month, day, hour, minute, second).timestamp(), timezone
    )


## Epoch
########################################################################################
def epoch_to_date_and_time(epoch: int) -> tuple:
    """
    Converts an epoch timestamp to a formatted date and time string.

    Args:
        epoch (int): The epoch timestamp to convert.

    Returns:
        tuple: A tuple containing the formatted date and time string in the format "YYYY-MM-DD HH:MM:SS" if the conversion is successful, otherwise a tuple containing "Invalid Date" and "Invalid Time".
    """
    try:
        return (
            f"{datetime.fromtimestamp(epoch).year}-{datetime.fromtimestamp(epoch).month}-{datetime.fromtimestamp(epoch).day} "
            f"{datetime.fromtimestamp(epoch).hour}:{datetime.fromtimestamp(epoch).minute}:{datetime.fromtimestamp(epoch).second}"
        )
    except:
        return ("Invalid Date", "Invalid Time")


def epoch_to_datetime(epoch: int) -> datetime:
    """
    Converts an epoch timestamp to a datetime object.

    Args:
        epoch (int): The epoch timestamp to convert.

    Returns:
        datetime: The corresponding datetime object if the conversion is successful, otherwise the current time.
    """
    try:
        return datetime.fromtimestamp(epoch)
    except:
        return datetime.now()


def epoch_to_RFC3339(epoch: int) -> str:
    """
    Converts an epoch timestamp to RFC3339 format.

    Args:
        epoch (int): The epoch timestamp to convert.

    Returns:
        str: The RFC3339 formatted timestamp if the conversion is successful, otherwise "Invalid Date".
    """
    try:
        return datetime.fromtimestamp(epoch).strftime("%Y-%m-%dT%H:%M:%SZ")
    except:
        return "Invalid Date"


def epoch_to_relative_time(epoch: int, timezone: str = "UTC") -> str:
    """
    Converts an epoch timestamp to a relative time string.

    Args:
        epoch (int): The epoch timestamp to convert.
        timezone (str, optional): The timezone to use for the conversion. Defaults to "UTC".

    Returns:
        str: The relative time string if the conversion is successful, otherwise "Invalid Date" or "Invalid Timezone" or "Future Date".

    """
    if timezone not in allowed_timezones:
        logger.error("Invalid timezone, Defaulting to UTC")
        timezone = "UTC"

    current_time = datetime.now(pytz.timezone(timezone))

    if epoch > current_time.timestamp():
        time_difference = current_time - datetime.fromtimestamp(
            epoch, tz=pytz.timezone(timezone)
        )

        diff_years = time_difference.days // 365
        diff_months = time_difference.days // 30
        diff_weeks = time_difference.days // 7
        diff_days = time_difference.days
        diff_hours = time_difference.seconds // 3600 % 24
        diff_minutes = time_difference.seconds // 60 % 60
        diff_seconds = time_difference.seconds % 60

        if diff_years > 0:
            if diff_years == 1:
                return "1 year from now"
            return f"{diff_years} years from now"

        if diff_months > 0:
            if diff_months == 1:
                return "1 month from now"
            return f"{diff_months} months from now"

        if diff_weeks > 0:
            if diff_weeks == 1:
                return "1 week from now"
            return f"{diff_weeks} weeks from now"

        if diff_days > 0:
            if diff_days == 1:
                return "1 day from now"
            return f"{diff_days} days from now"

        moved_diff_minutes = diff_minutes

        if diff_hours > 0:
            if diff_hours == 1:
                if moved_diff_minutes == 0:
                    return f"{diff_hours} hours from now"
                return f"1 hour from now, {moved_diff_minutes} minutes from now"
            if moved_diff_minutes == 0:
                return f"{diff_hours} hours from now"
            return f"{diff_hours} hours from now, {moved_diff_minutes} minutes from now"

        moved_diff_minutes = diff_minutes - 5

        if moved_diff_minutes > 0:
            if moved_diff_minutes == 1:
                if diff_seconds == 0:
                    return "1 minute from now"
                return f"1 minute from now, {diff_seconds} seconds from now"
            if diff_seconds == 0:
                return f"{moved_diff_minutes} minutes from now"
            return f"{moved_diff_minutes} minutes from now, {diff_seconds} seconds from now"

        if diff_seconds == 0:
            return "Just Now"

        if diff_seconds > 0:
            if diff_seconds == 1:
                return "1 second from now"
            return f"{diff_seconds} seconds from now"
    elif epoch == current_time.timestamp():
        return "Just Now"
    else:
        time_difference = current_time - datetime.fromtimestamp(
            epoch, tz=pytz.timezone(timezone)
        )

        diff_years = time_difference.days // 365
        diff_months = time_difference.days // 30
        diff_weeks = time_difference.days // 7
        diff_days = time_difference.days
        diff_hours = time_difference.seconds // 3600 % 24
        diff_minutes = time_difference.seconds // 60 % 60
        diff_seconds = time_difference.seconds % 60

        if diff_years > 0:
            if diff_years == 1:
                return "1 year ago"
            return f"{diff_years} years ago"

        if diff_months > 0:
            if diff_months == 1:
                return "1 month ago"
            return f"{diff_months} months ago"

        if diff_weeks > 0:
            if diff_weeks == 1:
                return "1 week ago"
            return f"{diff_weeks} weeks ago"

        if diff_days > 0:
            if diff_days == 1:
                return "1 day ago"
            return f"{diff_days} days ago"

        moved_diff_minutes = diff_minutes

        if diff_hours > 0:
            if diff_hours == 1:
                if moved_diff_minutes == 0:
                    return f"{diff_hours} hours ago"
                return f"1 hour ago, {moved_diff_minutes} minutes ago"
            if moved_diff_minutes == 0:
                return f"{diff_hours} hours ago"
            return f"{diff_hours} hours ago, {moved_diff_minutes} minutes ago"

        moved_diff_minutes = diff_minutes - 5

        if moved_diff_minutes > 0:
            if moved_diff_minutes == 1:
                if diff_seconds == 0:
                    return "1 minute ago"
                return f"1 minute ago, {diff_seconds} seconds ago"
            if diff_seconds == 0:
                return f"{moved_diff_minutes} minutes ago"
            return f"{moved_diff_minutes} minutes ago, {diff_seconds} seconds ago"

        if diff_seconds == 0:
            return "Just Now"

        if diff_seconds > 0:
            if diff_seconds == 1:
                return "1 second ago"
            return f"{diff_seconds} seconds ago"


# Color Conversion Functions
## Supported Formats: Hex, Color Name


def hex_to_color_name(hex: str) -> str:
    """
    Converts a hexadecimal color code to its corresponding color name.

    Args:
        hex (str): The hexadecimal color code.

    Returns:
        str: The corresponding color name if the conversion is successful, otherwise "Invalid Color".
    """
    try:
        return Color(hex).name
    except:
        return "Invalid Color"


def color_name_to_hex(color_name: str) -> str:
    """
    Converts a color name to its corresponding hexadecimal value.

    Args:
        color_name (str): The name of the color.

    Returns:
        str: The hexadecimal value of the closest matching color or "Invalid Color" if the color name is invalid.
    """
    try:
        hex_color = webcolors.name_to_hex(color_name)
    except:
        return "Invalid Color"

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
    # logger.info(date_and_time_to_RFC3339(2022, 1, 1, 0, 0, 0))
    # logger.info(RFC3339_to_datetime("2022-01-01T00:00:00.00Z"))
    # logger.info(datetime_to_RFC3339(datetime(2022, 1, 1, 0, 0, 0)))
    # logger.info(RFC3339_to_date_and_time("2022-01-01T00:00:00.00Z"))
    # logger.info(epoch_to_datetime(1732040151000 / 1000))
    # logger.info(datetime_to_epoch(datetime(2022, 1, 1, 0, 0, 0)))
    # logger.info(epoch_to_date_and_time(1640995200))
    # logger.info(date_and_time_to_epoch(2022, 1, 1, 0, 0, 0))
    # logger.info(date_and_time_to_relative_time(2024, 11, 19, 20, 15, 51, "Africa/Cairo"))
    # logger.info(RFC3339_to_relative_time("2024-11-19T22:29:20.00Z", "Africa/Cairo"))
    # logger.info(datetime_to_relative_time(datetime.now(), "Africa/Cairo"))
    # logger.info(epoch_to_relative_time(1732040151000 / 1000, "Africa/Cairo"))

    # logger.info(hex_to_color_name("#FF0000"))
    # logger.info(color_name_to_hex("red"))
    pass
