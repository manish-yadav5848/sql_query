
from pyspark.sql import SparkSession
from pyspark.sql.functions import *


def transform(spark: SparkSession, primary_key: list):

    beneficiary_vnq_wc_txt_df = spark.sql("SELECT plan_number, participant_id, beneficiary_id, type, relationship, relationship_other, substring(name, 0, 245) as name, street_address, street_address_2, city, state, zip, country, cast(date_of_birth as DATE), cast(primary_percentage_allocation as DECIMAL(5,2)), trustee, trust_date, date_format(to_date(batch_date, 'yyyyMMdd'), 'yyyy-MM-dd') as source_cycle_date,'NQ' as source_system FROM beneficiary_vnq_wc_txt")

    transform_df = beneficiary_vnq_wc_txt_df

    return transform_df