def get_initials(fio: str) -> str:
    """Returns two uppercase initial letters for avatar circles."""
    if not fio:
        return "АТ"
    parts = str(fio).strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif len(parts) == 1 and parts[0]:
        return parts[0][:2].upper()
    return "АТ"
