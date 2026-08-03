import numpy as np
import random
from faker import Faker
import pandas as pd
from datetime import datetime, timedelta



fake = Faker()

OUT_DIR = "data/raw"
NUM_MACHINE = 50
NUM_DAYS = 30

machine_types = [
    "Injection Molder",
    "Assembly Robot",
    "CNC Machine",
    "Packaging Machine",
    "Press Machine"
]

plants = ['Plant-A','Plant-B','Plant-C']


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
   machines_df.to_parquet(f"{OUT_DIR}/machines.parquet",index=False)

   print("Machines generated")

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
            "machine_id":machine.machine_id,
            "temperature":temp,
            "vibration" : vibration,
            "pressure":pressure,
            "rpm":random.uniform(1000,5000),
            "power_consumption":round(random.uniform(20,100),2),
            "failure_risk_score" : round(failure_risk,2)
           
        })
         current_time += timedelta(hours=1)

   telemetry_df = pd.DataFrame(telemetry)
   telemetry_df.to_parque(f"{OUT_DIR}/telemetry.parquet",index=False)

