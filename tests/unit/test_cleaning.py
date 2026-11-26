import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from glovo.silver.cleaning import city_key


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("unit-tests").getOrCreate()


def test_city_key_matches_every_spelling(spark):
    df = spark.createDataFrame([(" ŁÓDŹ ",), ("Lodz",), ("łódź",), ("KRAKÓW",)], "city string")
    result = [row.key for row in df.select(city_key(F.col("city")).alias("key")).collect()]
    assert result == ["lodz", "lodz", "lodz", "krakow"]


def test_city_key_keeps_empty_city_empty(spark):
    df = spark.createDataFrame([(None,)], "city string")
    assert df.select(city_key(F.col("city")).alias("key")).first().key is None
    