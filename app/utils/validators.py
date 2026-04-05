def validate_slot_str(v: str):
    if v is None:
        return v

    if len(v) != 5 or v[2] != ":":
        raise ValueError("slot must be in HH:MM format")

    hour, minute = v.split(":")
    if not hour.isdigit() or not minute.isdigit():
        raise ValueError("HH and MM should be digits")

    if int(hour) < 0 or int(hour) > 23:
        raise ValueError("HH must be between 00 and 23")
    if int(minute) not in (0, 15, 30, 45):
        raise ValueError("MM must be 00, 15, 30, or 45")

    return hour, minute
