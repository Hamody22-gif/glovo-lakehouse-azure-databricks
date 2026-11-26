"""Shared cleaning functions for the Silver layer."""

from pyspark.sql import Column
from pyspark.sql import functions as F

POLISH = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
ASCII = "acelnoszzACELNOSZZ"


def city_key(column: Column) -> Column:
    """Simplify a city name for matching: no Polish accents, no outer spaces, lowercase.

    Example: " ŁÓDŹ ", "Lodz" and "Łódź" all become "lodz".
    """
    return F.lower(F.trim(F.translate(column, POLISH, ASCII)))
 