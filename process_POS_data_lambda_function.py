import json
import boto3
import pandas as pd
from io import StringIO
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event["Records"][0]['s3']['object']['key']
    print(bucket_name,file_key)
    target_bucket = "xideralcinedata-processed"
    target_file = "pos_data_seq/pos_summary.csv"

    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)['Body'].read()
        csv_content = json.loads(response.decode('utf8'))
        # Leer CSV con manejo de errores
        try:
            df = pd.DataFrame(csv_content)
        except Exception as e:
            print("Error al leer el archivo CSV:", e)
            raise ValueError("El archivo CSV tiene un formato inválido")

        json_data = {
            "id": file_key.split(".")[0],
            "filas": str(df.shape[0]),
            "columnas": str(df.shape[1]),
            "columnas_NaN": str(df.columns[df.isnull().any()].tolist()),
        }

        # Manejo del archivo destino
        try:
            dest_file = s3.get_object(Bucket=target_bucket, Key=target_file)
            dest_content = json.loads(dest_file['Body'].read())
        except Exception as e:
            print("Error al cargar el archivo destino:", e)
            dest_content = []  # Inicializa como lista vacía si no existe o es inválido

        # Agregar nuevos datos y subir a S3
        dest_content.append(json_data)
        dest_csv = pd.DataFrame(dest_content)
        csv_buffer = StringIO()
        dest_csv.to_csv(csv_buffer, index=False)

        s3.put_object(Bucket=target_bucket, Key=target_file, Body=csv_buffer.getvalue())

        return {
            'statusCode': 200,
            'body': "CSV processed with file " + file_key
        }

    except Exception as e:
        print("Error general:", e)
        return {
            'statusCode': 500,
            'body': json.dumps("ERROR: " + str(e))
        }
