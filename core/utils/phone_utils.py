import phonenumbers


def format(raw: str) -> str:
    number = phonenumbers.parse(raw)
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
