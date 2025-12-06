def validate_slot_str(v: str):
    if v is None:
        return v

    if len(v) != 5 or v[2] != ":":
        raise ValueError("slot must be in HH:MM format")

    hour, minute = v.split(":")
    if not hour.isdigit() or not minute.isdigit():
        return ValueError("HH and MM should be digits")

    hour = int(hour)
    minute = int(minute)

    if hour < 0 or hour > 23:
        raise ValueError("HH must be between 00 and 23")
    if minute not in (0, 30):
        raise ValueError("MM must be 00 or 30")

    return hour, minute
