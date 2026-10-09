# Databricks notebook source
from pyspark.sql.functions import col, trim, to_timestamp, to_date, year, month, dayofmonth, when, regexp_replace, count
from pyspark.sql import functions as F

df_raw = spark.table("INPE.bronze.focos_raw")

df_silver = (
    df_raw
    .dropDuplicates(["id"])
    .withColumn("id", trim(col("id")))
    .withColumn("lat", trim(col("lat")).cast("double"))
    .withColumn("lon", trim(col("lon")).cast("double"))
    .withColumn("data_hora_gmt", to_timestamp(trim(col("data_hora_gmt")), "yyyy-MM-dd HH:mm:ss"))
    .withColumn("municipio_id", trim(col("municipio_id")).cast("int"))
    .withColumn("estado_id", trim(col("estado_id")).cast("int"))
    .withColumn("pais_id", trim(col("pais_id")).cast("int"))
    .withColumn("numero_dias_sem_chuva", trim(col("numero_dias_sem_chuva")).cast("int"))
    .withColumn("precipitacao", trim(col("precipitacao")).cast("double"))
    .withColumn("risco_fogo", trim(col("risco_fogo")).cast("double"))
    .withColumn("frp", trim(col("frp")).cast("double"))
    .withColumn("data", to_date(col("data_hora_gmt")))
    .withColumn("ano", year(col("data_hora_gmt")))
    .withColumn("mes", month(col("data_hora_gmt")))
    .withColumn("dia", dayofmonth(col("data_hora_gmt")))
    .withColumn("estado", regexp_replace("estado", "MARANHÃƒO", "MARANHÃO"))
    .withColumn("estado", regexp_replace("estado", "PARÃ", "PARÁ"))
    .withColumn("estado", regexp_replace("estado", "SÃƒO PAULO", "SÃO PAULO"))
    .withColumn("municipio", regexp_replace("municipio", "SÃƒO FÃ‰LIX DO XINGU", "SÃO FÉLIX DO XINGU"))
    .withColumn("municipio", regexp_replace("municipio", "LÃBREA", "LÁBREA"))
    .withColumn("municipio", regexp_replace("municipio", "PATROCÃNIO", "PATROCÍNIO"))
    .withColumn("bioma", regexp_replace("bioma", "AmazÃ´nia", "Amazônia"))
    .withColumn("bioma", regexp_replace("bioma", "Mata AtlÃ¢ntica", "Mata Atlântica"))
    .withColumn(
        "criticidade",
        when((col("risco_fogo") >= 0.8) & (col("frp") >= 100), "alta")
        .when((col("risco_fogo") >= 0.5) & (col("frp") >= 50), "media")
        .otherwise("baixa")
    )
    .withColumn("data_ref", F.to_date("data_hora_gmt"))
    .withColumn(
        "classe_risco",
        F.when(F.col("risco_fogo") >= 0.8, "ALTO")
         .when(F.col("risco_fogo") >= 0.4, "MEDIO")
         .otherwise("BAIXO")
    )
    .filter(F.col("lat").isNotNull() & F.col("lon").isNotNull())    
)

df_silver.write.mode("append").saveAsTable("INPE.silver.queimadas_focos")

df_quality = df_silver.select(
    count(when(col("id").isNull(), 1)).alias("id_nulo"),
    count(when(col("data_hora_gmt").isNull(), 1)).alias("data_nula"),
    count(when((col("lat") < -90) | (col("lat") > 90), 1)).alias("lat_invalida"),
    count(when((col("lon") < -180) | (col("lon") > 180), 1)).alias("lon_invalida"),
    count(when(col("frp") < 0, 1)).alias("frp_invalido")
)

display(df_quality)
