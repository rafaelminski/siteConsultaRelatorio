import duckdb
import time

print("Iniciando conversão... isso pode levar 1 ou 2 minutos.")
start = time.time()

# Substitua pelo nome exato do seu arquivo CSV gigante
nome_csv = "CreateAccounting_Relatório de Criação de Contabilidade.csv"

# O comando mágico: o DuckDB lê o CSV e cospe um Parquet compactado
duckdb.sql(f"""
    COPY (SELECT * FROM read_csv_auto('{nome_csv}', ignore_errors=true)) 
    TO 'dados_banco.parquet' (FORMAT 'parquet', COMPRESSION 'SNAPPY')
""")

end = time.time()
print(f"Sucesso! Arquivo 'dados_banco.parquet' criado em {end - start:.2f} segundos.")