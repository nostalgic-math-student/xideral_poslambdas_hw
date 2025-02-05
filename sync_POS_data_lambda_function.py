import json
import boto3
import pandas as pd
from io import StringIO
import os

s3_client = boto3.client('s3')


def lambda_handler(event, context):

    bucket_name = 'xideralcinedata'
    target_bucket = "xideralcinedata-processed"
    target_file = "pos_data/pos_summary.csv"

    try:
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        res_df = pd.DataFrame({},columns=["id","filas","columnas","columnas_NaN"])

        for pos_data_file in objects['Contents']:
            data = s3_client.get_object(Bucket=bucket_name,Key=pos_data_file['Key'])['Body'].read()
            csv_content = json.loads(data.decode('utf8'))
            df = pd.DataFrame(csv_content)
            json_data = {
            "id": pos_data_file['Key'].split(".")[0],
            "filas": str(df.shape[0]),
            "columnas": str(df.shape[1]),
            "columnas_NaN" : str(df.columns[df.isnull().any()].tolist()),
            }

            res_df = pd.concat([res_df, pd.DataFrame([json_data])], ignore_index=True)
        
        csv_buffer = StringIO()
        res_df.to_csv(csv_buffer,index=False)
        s3_client.put_object(Bucket=target_bucket, Key=target_file, Body=csv_buffer.getvalue())

        return {
        'statusCode': 200,
        'body': "CSV sync proccessed with files"
        }

    except Exception as e:
        print("Error:",e)
        return {
        'statusCode': 500,
        'body': json.dumps("ERROR:"+str(e))}