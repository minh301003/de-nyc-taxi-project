import argparse
from pyspark.sql import SparkSession

parser = argparse.ArgumentParser()

parser.add_argument('--input_green', required=True)
parser.add_argument('--input_yellow', required=True)
parser.add_argument('--output_green', required=True)
parser.add_argument('--output_yellow', required=True)

args = parser.parse_args()

input_green = args.input_green
input_yellow = args.input_yellow
output_green = args.output_green
output_yellow = args.output_yellow

# Create a Spark session
spark = SparkSession.builder \
    .appName('repartition-parquet') \
    .getOrCreate()

spark.conf.set('temporaryGcsBucket', 'dataproc-temp-asia-southeast1-779122383392-nde0solr')

# Function to check and convert to Parquet if necessary
def check_and_convert_to_parquet(df, input_path, output_path):
    try:
        df = spark.read.parquet(input_path)
    except Exception as e:
        print(f"File {input_path} is not a valid Parquet file: {e}")
        try:
            df = spark.read.csv(input_path, header=True, inferSchema=True)
            df.write.parquet(output_path, mode='overwrite')
            df = spark.read.parquet(output_path)
        except Exception as e:
            print(f"Failed to convert {input_path} to Parquet: {e}")
            return None
    return df

# Read and repartition the Parquet files
for month in range(1, 13):
    input_green_month = f"{input_green}/{month:02d}"
    input_yellow_month = f"{input_yellow}/{month:02d}"

    output_green_month = f"{output_green}/{month:02d}"
    output_yellow_month = f"{output_yellow}/{month:02d}"

    df_green = check_and_convert_to_parquet(spark, input_green_month, output_green_month)
    df_yellow = check_and_convert_to_parquet(spark, input_yellow_month, output_yellow_month)

    if df_green:
        df_green.repartition(4).write.parquet(output_green_month, mode='overwrite')
    if df_yellow:
        df_yellow.repartition(4).write.parquet(output_yellow_month, mode='overwrite')