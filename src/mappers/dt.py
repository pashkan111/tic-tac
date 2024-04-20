from datetime import datetime


def encode_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")


def decode_datetime(dt: str) -> datetime:
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f")
