# Smart Factory Data Platform — Architecture

## 1. Overview

This project implements a cloud-based **Smart Factory Data Platform** on Microsoft Azure.

The objective is to simulate a manufacturing environment and build a data platform capable of handling both **batch factory data** and **real-time machine telemetry**.

The platform combines:

* Synthetic data generation
* Azure Data Lake Storage Gen2 (ADLS Gen2)
* Azure Event Hubs
* Azure Data Factory
* Azure Databricks
* Databricks Serverless Compute
* Unity Catalog
* Spark Structured Streaming
* Bronze/Silver/Gold data processing
* Databricks SQL and operational dashboards

The architecture combines two complementary data flows:

1. **Batch processing flow** for factory/business datasets.
2. **Real-time streaming flow** for machine telemetry.

Azure Data Factory is used as an **orchestration layer** for the Databricks batch processing workflow, while Azure Event Hubs and Spark Structured Streaming handle the real-time telemetry path.

---

## 2. High-Level Architecture

```text
                         SMART FACTORY DATA PLATFORM
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
              Batch Data                 Real-Time Telemetry
                    │                           │
                    ▼                           ▼
          Synthetic Data Generator       Telemetry Generator
                    │                           │
                    ▼                           ▼
              ADLS Gen2                  Azure Event Hubs
                    │                           │
                    │                           ▼
                    │                 Databricks Structured
                    │                      Streaming
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
                         Azure Databricks
                         Serverless Compute
                                  │
                         ┌────────┴────────┐
                         │                 │
                    Batch Pipeline    Streaming Pipeline
                         │                 │
                         ▼                 ▼
                      Bronze ◄─────────────┘
                         │
                         ▼
                      Silver
                         │
                         ▼
                       Gold
                         │
                         ▼
                  Gold KPIs / Analytics
                         │
                         ▼
              Daily Operations Dashboard
```

The diagram represents the logical architecture. The batch orchestration and streaming ingestion paths are explained separately below.

---

## 3. Main Components

### 3.1 Synthetic Data Generator

Python scripts are used to generate synthetic Smart Factory data.

The generated data represents different aspects of a manufacturing environment, including:

* Machines
* Machine telemetry
* Maintenance
* Quality
* Deliveries
* Suppliers

The synthetic generator provides the data source used to demonstrate the data platform without requiring real industrial data.

---

### 3.2 Azure Data Lake Storage Gen2

ADLS Gen2 is the persistent storage layer of the platform.

The project uses the storage account:

`tfactorytelemetry`

It provides cloud storage for the data lake and its processing layers.

The data is organized according to a Bronze/Silver/Gold architecture.

```text
ADLS Gen2
│
├── Bronze
├── Silver
└── Gold
```

---

### 3.3 Azure Event Hubs

Azure Event Hubs provides the ingestion endpoint for real-time machine telemetry.

The telemetry generator continuously produces events and sends them to the configured Event Hub.

```text
Telemetry Generator
        │
        ▼
Azure Event Hubs
```

The Event Hub therefore acts as the entry point for the streaming telemetry pipeline.

---

### 3.4 Azure Data Factory

Azure Data Factory is used as the **orchestration layer** for the Databricks processing workflow.

The implemented pipeline executes Databricks notebooks sequentially.

The documented pipeline contains three main notebook activities:

```text
run_bronze_ingestion
        │
        ▼
run_transformation
        │
        ▼
run_gold_kpi
```

Each downstream notebook starts after the successful completion of the previous notebook.

Therefore, Data Factory is responsible primarily for **workflow orchestration**, while the actual data processing is performed by Databricks.

Screenshot:

`../screenshots/data-factory/pipeline_definition.png`

---

### 3.5 Azure Databricks

Azure Databricks is the main processing and analytics platform.

The project uses **Databricks Serverless Compute**, rather than a user-managed Spark cluster.

Databricks is responsible for:

* Data ingestion
* Spark processing
* Structured Streaming
* Data cleaning
* Data transformation
* Bronze/Silver/Gold processing
* KPI generation
* Analytics

The Databricks workspace contains the notebooks used by the Data Factory pipeline as well as notebooks used for the streaming workflow.

---

### 3.6 Unity Catalog

Unity Catalog provides the data governance and organization layer inside Databricks.

It is used to manage:

* Catalogs
* Schemas
* Tables
* Storage credentials
* External locations

The logical relationship is:

```text
Unity Catalog
      │
      ├── Catalogs
      │      │
      │      └── Schemas
      │              │
      │              └── Tables
      │
      ├── Storage Credentials
      │
      └── External Locations
```

---

## 4. Batch Data Flow

The batch processing workflow begins with generated factory data.

```text
Synthetic Data
      │
      ▼
ADLS Gen2
      │
      ▼
Azure Data Factory
      │
      ▼
run_bronze_ingestion
      │
      ▼
Bronze
      │
      ▼
run_transformation
      │
      ▼
Silver
      │
      ▼
run_gold_kpi
      │
      ▼
Gold / KPIs
      │
      ▼
Dashboard
```

### Step 1 — Data Generation

Synthetic factory datasets are generated using Python.

### Step 2 — Data Storage

The generated data is stored in the ADLS Gen2 data lake.

### Step 3 — Orchestration

Azure Data Factory starts the Databricks processing workflow.

### Step 4 — Bronze Ingestion

The `run_bronze_ingestion` Databricks notebook handles the Bronze ingestion stage.

### Step 5 — Transformation

After the Bronze notebook completes successfully, ADF triggers `run_transformation`.

This stage performs the required data cleaning and transformations to produce the next processing layer.

### Step 6 — Gold KPI Generation

After the transformation stage completes, ADF triggers `run_gold_kpi`.

This stage prepares the KPI/analytics layer used by the dashboard.

---

## 5. Real-Time Telemetry Flow

The platform also implements a separate streaming path for machine telemetry.

```text
Telemetry Generator
        │
        ▼
Azure Event Hubs
        │
        ▼
Databricks Structured Streaming
        │
        ▼
Bronze
        │
        ▼
Silver / Gold
        │
        ▼
Analytics
```

The telemetry producer sends events to Azure Event Hubs.

Databricks consumes these events using Spark Structured Streaming.

The streaming workflow uses the Spark streaming APIs:

```python
spark.readStream
```

to define the streaming source and:

```python
writeStream
```

to start and configure the streaming query.

This streaming path is conceptually separate from the ADF notebook orchestration shown in the batch pipeline.

---

## 6. Medallion Architecture

The data processing architecture follows the Bronze/Silver/Gold pattern.

### Bronze

The Bronze layer contains raw or minimally processed data.

Its purpose is to preserve an ingestion-level representation of the source data.

Examples include:

* Machine data
* Telemetry
* Maintenance
* Quality
* Deliveries
* Suppliers

---

### Silver

The Silver layer contains cleaned and transformed data.

Typical operations include:

* Data type conversion
* Cleaning
* Validation
* Null handling
* Standardization
* Deduplication
* Data enrichment

The exact transformations are implemented in the Databricks notebooks.

---

### Gold

The Gold layer contains analytics-ready data.

This layer is designed for:

* KPIs
* Aggregations
* Operational analysis
* Dashboard consumption

The `run_gold_kpi` notebook is responsible for generating the KPI-oriented Gold layer used by the analytics layer.

---

## 7. Orchestration vs Processing

An important architectural distinction in this project is the separation between **orchestration** and **data processing**.

### Azure Data Factory

Responsible for:

* Starting the workflow
* Executing Databricks notebooks
* Controlling execution order
* Passing execution from one stage to the next

### Azure Databricks

Responsible for:

* Reading data
* Processing data
* Transforming data
* Running Spark jobs
* Running Structured Streaming
* Producing Bronze/Silver/Gold datasets
* Generating analytics outputs

The relationship can therefore be summarized as:

```text
             Azure Data Factory
                    │
             Orchestration
                    │
                    ▼
             Azure Databricks
                    │
              Data Processing
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Bronze    Silver     Gold
```

---

## 8. Data Governance

Databricks Unity Catalog provides governance for the data stored in the platform.

The storage access architecture is:

```text
Databricks
     │
     ▼
Unity Catalog
     │
     ├── Storage Credential
     │
     ▼
External Location
     │
     ▼
ADLS Gen2
```

This separates data governance and access management from the processing logic.

---

## 9. Analytics Layer

The processed Gold data is used to produce operational analytics.

```text
Gold Data
    │
    ▼
KPI / SQL Queries
    │
    ▼
Daily Operations Dashboard
```

The project includes a Daily Operations Dashboard that provides a visual representation of the processed factory data.

Screenshot:

`../screenshots/databricks/daily_operations_dashboard.png`

---

## 10. Architecture Summary

The Smart Factory platform can be summarized as four main layers:

```text
┌──────────────────────────────────────────┐
│              DATA SOURCES                │
│                                          │
│ Synthetic Data + Machine Telemetry       │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│              INGESTION                   │
│                                          │
│ ADLS Gen2 + Azure Event Hubs             │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│             PROCESSING                  │
│                                          │
│ ADF Orchestration + Databricks           │
│ Serverless + Structured Streaming        │
│                                          │
│ Bronze → Silver → Gold                   │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│              ANALYTICS                   │
│                                          │
│ Gold KPIs + Databricks Dashboard         │
└──────────────────────────────────────────┘
```

The resulting architecture demonstrates a complete cloud data engineering workflow combining **batch processing, real-time streaming, orchestration, data lake storage, distributed processing, governance, and analytics**.
