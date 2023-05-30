
from pyspark.sql import SparkSession
from pyspark.sql.functions import *


def transform(spark: SparkSession, primary_key: list):

    consumption_df = spark.sql("select coalesce(nullif(M.rep_tax_id_ssn, ''), '-9999') as rep_tax_id_ssn, coalesce(nullif(M.plan_number, ''), '-9999') as plan_number, coalesce(nullif(M.fund_number, ''), '-9999') as fund_number, M.producer_role_code, M.producer_role_type, coalesce(M.source_cycle_date, current_date() -1) as source_cycle_date, cast(M.cash_value_amount as Decimal(17, 2)) as cash_value_amount, cast(M.ee_cash_value_amount as Decimal(17, 2)) as ee_cash_value_amount, cast(M.er_cash_value_amount as Decimal(17, 2)) as er_cash_value_amount, cast(M.ytd_contributions as Decimal(17, 2)) as ytd_contributions, cast(M.total_units as Decimal(17, 4)) as total_units, case when t1.fund_number='-9999' then cast('0' as decimal(17,4)) else cast(t1.unit_price[0] AS DECIMAL(17, 4)) end  AS unit_price from ( ( select P.rep_tax_id_ssn, P.plan_number, B.fund_number, P.producer_role_code, P.producer_role_type, coalesce(B.source_cycle_date, current_date() -1) as source_cycle_date, B.cash_value_amount, B.ee_cash_value_amount, B.er_cash_value_amount, B.ytd_contributions, B.total_units, B.unit_price as unit_price from ( select rep_tax_id_ssn, concat_ws ( ';', collect_set (distinct (nullif(producer_role_code_desc, ''))) ) as producer_role_code, concat_ws ( ';', collect_set ( distinct ( nullif( case when producer_role_type = 'RIA/IAR' then producer_role_type else substring(producer_role_type, 0, 3) end, '' ) ) ) ) as producer_role_type, plan_number from producer where AGREEMENT_LEVEL_CODE = 'PLAN' group by rep_tax_id_ssn, plan_number ) P inner join ( SELECT coalesce(t1.plan_number, '-9999') as plan_number, coalesce(t1.fund_number, '-9999') as fund_number, coalesce(t1.source_cycle_date, current_date() -1) as source_cycle_date, sum(coalesce(cash_value, 0)) as cash_value_amount, sum(coalesce(ee_cash_value, 0)) as ee_cash_value_amount, sum(coalesce(er_cash_value, 0)) as er_cash_value_amount, sum(coalesce(ytd_contributions, 0)) as ytd_contributions, sum(coalesce(number_of_units, 0)) as total_units, collect_set (Unit_price) as Unit_price from ( SELECT pc.plan_number, pc.source_cycle_date, trim(pc.fund_number) as fund_number, coalesce(pc.cash_value, 0) as cash_value, coalesce(pc.number_of_units, 0) as number_of_units, coalesce(pc.ytd_contributions, 0) as ytd_contributions, pc.Unit_price as Unit_price, case when pc.cash_value = null then 0 when pc.money_type_description = 'EE' then cash_value end as ee_cash_value, case when pc.cash_value = null then 0 when pc.money_type_description = 'ER' then cash_value end as er_cash_value from participant_core_balance pc ) as T1 GROUP BY plan_number, source_cycle_date, fund_number ) B on coalesce(B.plan_number, '-9999') = coalesce(P.plan_number, '-9999') ) union ( select m1.rep_tax_id_ssn, m1.plan_number, m1.fund_number, concat_ws ( ';', array_distinct ( flatten (collect_set (distinct (producer_role_code))) ) ) as producer_role_code, concat_ws ( ';', array_distinct ( flatten (collect_set (distinct (producer_role_type))) ) ) as producer_role_type, coalesce(m1.source_cycle_date, current_date() -1) as source_cycle_date, sum(coalesce(m1.cash_value, 0)) as cash_value_amount, sum(coalesce(m1.ee_cash_value, 0)) as ee_cash_value_amount, sum(coalesce(m1.er_cash_value, 0)) as er_cash_value_amount, sum(coalesce(m1.ytd_contributions, 0)) as ytd_contributions, sum(coalesce(m1.number_of_units, 0)) as total_units, collect_set(unit_price) as unit_price from ( SELECT pr.rep_tax_id_ssn, pr.producer_role_code, pr.producer_role_type, pc.participant_id, pr.plan_number, trim(pc.fund_number) as fund_number, pc.source_cycle_date, coalesce(pc.cash_value, 0) as cash_value, coalesce(pc.ytd_contributions, 0.00) as ytd_contributions, pc.er_cash_value, pc.ee_cash_value, pc.number_of_units, unit_price[0] as unit_price from ( select rep_tax_id_ssn, participant_id, collect_set (distinct (nullif(producer_role_code_desc, ''))) as producer_role_code, collect_set ( distinct ( nullif( case when producer_role_type = 'RIA/IAR' then producer_role_type else substring(producer_role_type, 0, 3) end, '' ) ) ) as producer_role_type, plan_number from producer where AGREEMENT_LEVEL_CODE = 'MSRC' OR AGREEMENT_LEVEL_CODE = 'PART' group by rep_tax_id_ssn, participant_id, plan_number ) pr inner join ( select participant_id, plan_number, source_cycle_date, fund_number, sum(cash_value) as cash_value, sum(er_cash_value) as er_cash_value, sum(ee_cash_value) as ee_cash_value, sum(number_of_units) as number_of_units, collect_set (unit_price) as unit_price, sum(ytd_contributions) as ytd_contributions from ( select source_cycle_date, participant_id, plan_number, fund_number, number_of_units, ytd_contributions, cash_value, unit_price, case when money_type_description = 'EE' then cash_value end as ee_cash_value, case when money_type_description = 'ER' then cash_value end as er_cash_value from participant_core_balance ) group by participant_id, plan_number, fund_number, source_cycle_date ) pc on coalesce(pc.plan_number, '-9999') = coalesce(pr.plan_number, '-9999') and coalesce(pc.participant_id, '-9999') = coalesce(pr.participant_id, '-9999') ) m1 group by m1.rep_tax_id_ssn, m1.plan_number, m1.fund_number, source_cycle_date ) ) as M")

    return consumption_df
