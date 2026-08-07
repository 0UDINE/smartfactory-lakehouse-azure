import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.eventhub import EventHubProducerClient, EventData, TransportType
import uuid
import random
from datetime import datetime, timezone
import json
import time

load_dotenv()

TENANT_ID = os.environ["AZURE_TENANT_ID"]
CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
FULL_EVENT_HUB_NAMESPACE = os.environ["AZURE_EVENT_HUBS_FULL_NAMESPACE"]
EVENT_HUB_NAME = os.environ["AZURE_EVENT_HUB_NAME"]
NUM_MACHINE = 50

credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)

producer = EventHubProducerClient(
    fully_qualified_namespace=FULL_EVENT_HUB_NAMESPACE,
    eventhub_name=EVENT_HUB_NAME,
    credential=credential,
    transport_type=TransportType.AmqpOverWebsocket
)

batch = producer.create_batch()

MACHINES_ID = [f"MCH-{1000+i}" for i in range(NUM_MACHINE)]

def generate_event() -> dict :
    machine_id = random.choice(MACHINES_ID)
    temperature = random.uniform(30,90)
    vibration = random.uniform(0.2,1.5)
    pressure = random.uniform(80,120)
    rpm = random.uniform(1000,5000)
    power_consumption = random.uniform(20,100)

    anomaly = random.random() < 0.3

    if anomaly :
        temperature += random.uniform(20, 45)
        vibration += random.uniform(2.5, 5.5)
        pressure += random.uniform(15, 35)

    failure_risk_score = min(
        0.99,
        + (0.25 if temperature > 100 else 0)  # +0.25 if temp is too high
        + (0.35 if vibration > 4 else 0)      # +0.35 if vibration is too high
        + (0.2 if pressure > 130 else 0)      # +0.20 if pressure is too high
        + random.uniform(0, 0.25)             # + a random 0.00-0.25 "noise" component
    )

    return {
        "event_id":str(uuid.uuid4()),
        "timestamp" : datetime.now(timezone.utc).isoformat(),
        "machine_id":machine_id,
        "temperature":temperature,
        "vibration":vibration,
        "pressure":pressure,
        "rpm":rpm,
        "power_cosumption":power_consumption,
        "failure_risk_score":failure_risk_score,
        "is_anomaly": anomaly,
        "source": "smartFactory-simulator"
    }

def main() -> None :
    print("Starting FactoryPulse IoT producer. Press CTRL+C to stop.")

    try:
        while True :
            event_batch = producer.create_batch()
            for _ in range(10):
                event_data = generate_event()
                event_batch.add(EventData(json.dumps(event_data)))
                print(event_data)

            producer.send_batch(event_batch)
            print("sent 10 telemetry events")
            time.sleep(5)
    finally:
        producer.close()


if __name__ == "__main__":
    main()
