from strsimpy.jaro_winkler import JaroWinkler

LOCATIONS = [
    "zilukha",
    "langjophakha",
    "babesa",
    "motithang",
    "taba",
    "pamtsho",
    "hejo",
    "dechencholing",
    "ngabiphu",
    "kabesa",
    "serbithang",
    "changjiji",
    "changzamtog",
    "changbangdu",
    "chamgang",
    "depsi",
    "dangrena",
    "olakha",
    "main town",
    "changangkha",
    "bebena",
    "simtokha",
    "changjalu",
    "samteling",
    "chubachu",
    "jungshina",
    "rtc",
    "lungtenphu",
    "kala bazaar",
]


def check_taba(location):
    if "taba" in location:
        return True
    return False


def check_town(location):
    if "town" in location:
        return True
    return False


def remove_identifiers(location):
    if "upper" in location:
        location = location.replace("upper", "")
    if "lower" in location:
        location = location.replace("lower", "")
    return location


"""
Have a standardized list of locations (standardized_locations.csv): standardized according to my standards
and then check the similarity for each of the strings and replace only if similarity greater than 0.75
if not 0.75 then we would be replacing completely different locations. 0.75 is a good threshold from analyzing listings collected till date (approximately 233)
"""


def find_closest_standard_location(location: str):
    jaro = JaroWinkler()
    correct_location = ""
    max_similarity = 0
    for standardized_location in LOCATIONS:
        similarity = jaro.similarity(location, standardized_location)
        if similarity > max_similarity:
            max_similarity = similarity
            correct_location = standardized_location
    if max_similarity > 0.75:
        return correct_location
    else:
        return location


def get_standard_location(location: str):
    location = str(location).lower().strip()
    location = remove_identifiers(location)
    if location in LOCATIONS:
        return location
    elif location == "babena":
        return "bebena"
    elif check_taba(location):
        return "taba"
    elif check_town(location):
        return "main town"
    elif location == "nan":
        return ""
    else:
        return find_closest_standard_location(location)
