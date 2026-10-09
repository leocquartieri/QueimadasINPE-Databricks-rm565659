# Databricks notebook source
# Camada Gold — agregações publicadas no Azure MySQL Flexible Server
from pyspark.sql.functions import count, avg, max as spark_max

# Preencha o host (saída "mysql_fqdn" do Terraform) e a senha (a mesma do secret MYSQL_ADMIN_PASSWORD).
# Não suba a senha para o GitHub: prefira um secret scope do Databricks, se disponível:
# mysql_password = dbutils.secrets.get("queimadas-scope", "mysql-admin-password")
mysql_host = "<mysql-queimadas-xxxxxx.mysql.database.azure.com>"
mysql_port = "3306"
mysql_db = "queimadas"
mysql_user = "queimadasadmin"
mysql_password = "<senha>"

df_silver = spark.table("inpe.silver.queimadas_focos")

gold_estado_dia = (
    df_silver.groupBy("data", "estado")
    .agg(
        count("*").alias("qtd_focos"),
        avg("frp").alias("frp_medio"),
        avg("risco_fogo").alias("risco_medio")
    )
)

gold_bioma_dia = (
    df_silver.groupBy("data", "bioma")
    .agg(
        count("*").alias("qtd_focos"),
        avg("frp").alias("frp_medio")
    )
)

gold_municipios_criticidade = (
    df_silver.groupBy("estado", "municipio")
    .agg(
        count("*").alias("qtd_focos"),
        avg("frp").alias("frp_medio"),
        avg("risco_fogo").alias("risco_medio"),
        spark_max("frp").alias("frp_max")
    )
)

for df_out, table_name in [
    (gold_estado_dia, "gold_focos_estado_dia"),
    (gold_bioma_dia, "gold_focos_bioma_dia"),
    (gold_municipios_criticidade, "gold_municipios_criticidade"),
]:
    (
        df_out.write
        .format("mysql")
        .option("host", mysql_host)
        .option("port", mysql_port)
        .option("database", mysql_db)
        .option("dbtable", table_name)
        .option("user", mysql_user)
        .option("password", mysql_password)
        .option("useSSL", "true")
        .option("requireSSL", "true")
        .mode("overwrite")
        .save()
    )
    print(f"{table_name}: publicada")
