import duckdb
import os

# Nome do seu arquivo parquet atual
input_file = 'dados_banco.parquet'

# Verifica se existe
if not os.path.exists(input_file):
    print("Erro: Arquivo dados_banco.parquet não encontrado!")
else:
    print("Iniciando fatiamento...")
    # Conecta no DuckDB
    con = duckdb.connect()
    
    # Exporta dividindo em arquivos de aproximadamente 500.000 linhas (ajuste seguro para ficar <100MB)
    # Isso vai criar arquivos: dados_part_0.parquet, dados_part_1.parquet, etc.
    con.execute(f"""
        COPY (SELECT * FROM '{input_file}') 
        TO 'dados_part_' (FORMAT PARQUET, PER_THREAD_OUTPUT TRUE, FILE_SIZE_BYTES 90000000)
    """)
    
    print("Sucesso! Arquivos 'dados_part_*.parquet' criados.")
    print("Agora você pode apagar o 'dados_banco.parquet' original e o CSV para subir no GitHub.")