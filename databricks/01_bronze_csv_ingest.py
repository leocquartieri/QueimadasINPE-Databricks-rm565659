# Databricks notebook source
# Camada Bronze — ingestão "raw" do CSV colocado no volume /Volumes/inpe/bronze/arquivo
from pyspark.sql import Row
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, TimestampType, LongType
)
from datetime import datetime

VOLUME_PATH = "/Volumes/inpe/bronze/arquivo"

dbutils.widgets.text("input_file_path", "")
input_file_path = dbutils.widgets.get("input_file_path")

# O gatilho "File arrival" não informa o caminho do arquivo. Sem parâmetro,
# processamos o CSV mais recente do volume que ainda não consta na auditoria.
if not input_file_path:
    spark.sql("""
        CREATE TABLE IF NOT EXISTS inpe.bronze.auditoria_ingestao (
            data_processamento STRING, arquivo_origem STRING,
            caminho_arquivo STRING, status STRING)
    """)
    ja_processados = {
        r.caminho_arquivo
        for r in spark.table("inpe.bronze.auditoria_ingestao").select("caminho_arquivo").collect()
    }
    pendentes = [
        f for f in dbutils.fs.ls(VOLUME_PATH)
        if f.name.lower().endswith(".csv") and f.path.replace("dbfs:", "") not in ja_processados
    ]
    if not pendentes:
        dbutils.notebook.exit("Nenhum arquivo novo no volume.")
    mais_recente = max(pendentes, key=lambda f: f.modificationTime)
    input_file_path = mais_recente.path.replace("dbfs:", "")

file_name = input_file_path.split("/")[-1]
print("Processando:", input_file_path)

schema = StructType([
    StructField("id", StringType()),
    StructField("lat", DoubleType()),
    StructField("lon", DoubleType()),
    StructField("data_hora_gmt", TimestampType()),
    StructField("satelite", StringType()),
    StructField("municipio", StringType()),
    StructField("estado", StringType()),
    StructField("pais", StringType()),
    StructField("municipio_id", LongType()),
    StructField("estado_id", LongType()),
    StructField("pais_id", LongType()),
    StructField("numero_dias_sem_chuva", LongType()),
    StructField("precipitacao", DoubleType()),
    StructField("risco_fogo", DoubleType()),
    StructField("bioma", StringType()),
    StructField("frp", DoubleType()),
])

df_bronze = (
    spark.read
    .option("header", True)
    .option("encoding", "UTF-8")
    .schema(schema)
    .csv(input_file_path)
)

display(df_bronze)
df_bronze.printSchema()

df_bronze.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable("inpe.bronze.focos_raw")

# Auditoria só depois da carga bem-sucedida
spark.createDataFrame([Row(
    data_processamento=str(datetime.now()),
    arquivo_origem=file_name,
    caminho_arquivo=input_file_path,
    status="sucesso",
)]).write.mode("append").saveAsTable("inpe.bronze.auditoria_ingestao")
