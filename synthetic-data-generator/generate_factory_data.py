import numpy as np
import random
from faker import Faker
import pandas as pd
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobBlock, BlobClient, StandardBlobTier
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STIRNG"]
CONTAINER = "bronze"

fake = Faker()

OUT_DIR = Path("./data/raw")
OUT_DIR.mkdir(exist_ok=True)

NUM_MACHINE = 50
NUM_DAYS = 30
NUM_SUPPLIERS = 20

machine_types = [
    "Injection Molder",
    "Assembly Robot",
    "CNC Machine",
    "Packaging Machine",
    "Press Machine"
]

plants = ['Plant-A','Plant-B','Plant-C']

def upload_to_blob(file_path: Path):
   client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
   blob_client = client.get_blob_client(
      container=CONTAINER,
      blob=file_path.name
   )

   with open(file_path, "rb") as f:
      blob_client.upload_blob(f, overwrite=True)
      print(f"{file_path.name} uploaded successfully")

machines = []

for i in range(NUM_MACHINE):
   machines.append({
      "machine_id" : f"MCH-{1000+i}",
      "machine_type" :random.choice(machine_types),
      "plant" : random.choice(plants),
      "installation_date" : fake.date_between(
         start_date = "-5y",
         end_date ="-1y"
      ),
      "status":random.choice(['ACTIVE','MAINTENANCE']),
      "manufacturer":fake.company(),
      "maintenance_cycle_days":random.choice([30,60,90])
   })

machines_df = pd.DataFrame(machines)
parquet_path = OUT_DIR / "machines.parquet"
machines_df.to_parquet(parquet_path,index=False)
upload_to_blob(parquet_path)

print("Machines generated and stored")

telemetry = []

start_time = datetime.now() - timedelta(days=NUM_DAYS)

for machine in machines :
   current_time = start_time
   for _ in range(NUM_DAYS):
      temp = random.uniform(30,90)
      vibration = random.uniform(0.2,1.5)
      pressure = random.uniform(80,120)

      failure_risk = 0

      # anomaly injection
      if random.random() < 0.3 :
         temp += random.uniform(20,40)
         vibration += random.uniform(2,5)
         failure_risk += random.uniform(0.7,0.99)

      telemetry.append({
         "timestamp":current_time,
         "machine_id":machine["machine_id"],
         "temperature":temp,
         "vibration" : vibration,
         "pressure":pressure,
         "rpm":random.uniform(1000,5000),
         "power_consumption":round(random.uniform(20,100),2),
         "failure_risk_score" : round(failure_risk,2)
           
      })
      current_time += timedelta(hours=1)

telemetry_df = pd.DataFrame(telemetry)
parquet_path = OUT_DIR / "Iot_telemetry.parquet"
telemetry_df.to_parquet(parquet_path,index=False)
upload_to_blob(parquet_path)

print("Telemetry generated and stored")

suppliers = []

for i in range(NUM_SUPPLIERS):
   suppliers.append({
      "supplier_id":f"SUP-{100+i}",
      "supplier_name":fake.company(),
      "country":fake.country(),
      "quality_score" : round(random.uniform(70,100),2)
   })

suppliers_df = pd.DataFrame(suppliers)
parquet_path = OUT_DIR / "suppliers.parquet"
suppliers_df.to_parquet(parquet_path,index=False)
upload_to_blob(parquet_path)

print("Suppliers generated and stored")

deleveries = []

for i in range(100):
   expected = fake.date_between(
      start_date="-30d",
      end_date="now"
   )

   delay = random.choice([0, 0, 0, 2, 3, 5, 10, 24])

   actual = expected + timedelta(hours=delay)

   deleveries.append({
      "delevery_id":f"DEL-{10000+i}",
      "supplier_id":random.choice(
         suppliers_df["supplier_id"].tolist()
      ),
      "material_id":f"MAT-{random.randint(100,300)}",
      "expected_delevery_date" : expected,
      "actual_delevery_date":actual,
      "delay_hours":delay,
      "quality_score":round(random.uniform(70,100),2)
   })   

deleveries_df = pd.DataFrame(deleveries)
parquet_path = OUT_DIR / "deleveries.parquet"
deleveries_df.to_parquet(parquet_path,index=False)
upload_to_blob(parquet_path)

print("Deleveries generated and stored")

maintenance_logs= []

for i in range(500):
      maintenance_logs.append({
         "maintenance_id":f"MAIN-{1000+i}",
         "machine_id":random.choice(machines_df["machine_id"].tolist()),
         "maintenance_type":  random.choice([
            "Preventive",
            "Corrective",
            "Emergency"
         ]),
         "failure_reason":random.choice([
            "Overheating",
            "Bearing Failure",
            "Sensor Fault",
            "Hydraulic Leak"
         ]),
         "repair_duration_hours":round(
            random.uniform(1,12),
            2
         ),
         "technicien": fake.name(),
         "cost":round(random.uniform(100,5000),2)
      })

maintenance_logs_df = pd.DataFrame(maintenance_logs)
parquet_path = OUT_DIR / "maintenance.parquet"
maintenance_logs_df.to_parquet(parquet_path,index=False)
upload_to_blob(parquet_path)

print("Maintanence logs generated and stored")

quality = []

for i in range(1000):
   severity = random.choice([
      "LOW",
      "MEDIUM"
      "HIGH",
   ])

   quality.append({
      "inspection_id" :f"Q-{1000+i}",
      "batch_id" : f"BATCH-{random.uniform(1000,5000)}",
      "detect_type" : random.choice([
         "Surface Defect",
         "Alignement Issue",
         "Crack",
         "Electrical Fault"
      ]),
      "severity": severity,
      "detected_at": fake.date_between(
         start_date="-30d",
         end_date="now"
      ),
      "root_cause":random.choice([
         "Temperature",
         "Supplier Material",
         "Operator Error",
         "Machine Caliberation"
      ])
   })

quality_df = pd.DataFrame(quality)
parquet_path = OUT_DIR / "quality.parquet"
quality_df.to_parquet(parquet_path,index=False)
upload_to_blob(parquet_path)

print("Quality inspections generated and stored")

print("ALL DATASETS GENERATED SUCCESSFULLY")

   