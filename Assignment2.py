import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.types import StringType, StructField, StructType

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("CDCDataLoader") \
    .getOrCreate()

# Define schema for objects_detection_events
objects_detection_schema = StructType([
    StructField("vehicle_id", StringType(), True),
    StructField("detection_time", StringType(), True),
    StructField("detections", StringType(), True)
])

# Define schema for vehicle_status
vehicle_status_schema = StructType([
    StructField("vehicle_id", StringType(), True),
    StructField("report_time", StringType(), True),
    StructField("status", StringType(), True)
])

# Define a class for file system event handling
class FileHandler(FileSystemEventHandler):
    def __init__(self, spark):
        self.spark = spark

    def on_created(self, event):
        if event.is_directory:
            return
        filename = event.src_path
        if 'objects_detection_events' in filename:
            objects_detection_df = self.spark.read.json(filename, schema=objects_detection_schema)
            objects_detection_df = objects_detection_df.withColumn("detections", explode(objects_detection_df.detections))
            objects_detection_df = objects_detection_df.select(
                "vehicle_id",
                "detection_time",
                "detections.object_type",
                "detections.object_value"
            )
            # Write objects_detection DataFrame to PostgreSQL
            objects_detection_df.write \
                .format("jdbc") \
                .option("url", "jdbc:postgresql://your_postgresql_host:5432/your_database") \
                .option("dbtable", "objects_detection_table") \
                .option("user", "your_username") \
                .option("password", "your_password") \
                .save()
        elif 'vehicle_status' in filename:
            vehicle_status_df = self.spark.read.json(filename, schema=vehicle_status_schema)
            # Write vehicle_status DataFrame to PostgreSQL
            vehicle_status_df.write \
                .format("jdbc") \
                .option("url", "jdbc:postgresql://your_postgresql_host:5432/your_database") \
                .option("dbtable", "vehicle_status_table") \
                .option("user", "your_username") \
                .option("password", "your_password") \
                .save()

# Set up file system event handler
event_handler = FileHandler(spark)
observer = Observer()
observer.schedule(event_handler, path='/path/to/watch', recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    observer.join()

# Stop the SparkSession
spark.stop()