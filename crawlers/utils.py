from unidecode import unidecode


class IncorrectArgsException(Exception):
    pass


def parse_city(city: str) -> str:
    """
    Parses the name of a given city, removing special characters and replacing empty spapces with "-"
    :param city: São Paulo
    :return: sao-paulo
    """
    parsed_city = unidecode(city.lower().replace(' ', '-'))
    return parsed_city
