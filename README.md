# **ETL Pipeline for MongoDB to MySQL Data Migration**

This project implements an **ETL (Extract, Transform, Load)** pipeline to migrate data from **MongoDB** to a **MySQL** relational database. The pipeline is designed to handle complex JSON data, flatten it, and transform it into a structured format suitable for relational databases. The project also includes a notification system for job failures and optimizations for query performance.

---

## **Table of Contents**

1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Key Features](#key-features)
4. [Setup and Installation](#setup-and-installation)
5. [Running the ETL Pipeline](#running-the-etl-pipeline)
6. [Database Model](#database-model)
7. [Sample Data](#sample-data)
8. [Documentation](#documentation)
9. [License](#license)

---

## **Project Overview**

The goal of this project is to migrate data from MongoDB (unstructured JSON) to a MySQL database (structured relational format). The ETL pipeline performs the following tasks:

1. **Extract**: Reads JSON data from MongoDB collections.
2. **Transform**: Flattens and transforms the JSON data into a structured format.
3. **Load**: Loads the transformed data into a MySQL database.

The project also includes:

- A **notification system** to alert stakeholders of ETL job failures.
- **Query performance optimizations** through indexing and database design.
- A **normalized database model** to ensure data integrity and avoid redundancy.

---

## **Directory Structure**

```
.
├── config/                  # Configuration files for the project
├── connections/             # Connectors for MongoDB and MySQL
├── dags/                    # Airflow DAG for the ETL pipeline
├── data/                    # Sample input (JSON) and output (CSV) data
│   ├── output_sample/       # Sample flattened data in CSV format
│   └── source_sample/       # Sample JSON data from MongoDB
├── Docs/                    # Documentation files
├── etl/                     # ETL pipeline scripts (extract, transform, load)
├── main.py                  # Main script to run the ETL pipeline
├── models/                  # Database models for MongoDB and MySQL
├── notebook/                # Jupyter notebook for exploratory analysis
├── scripts/                 # Utility scripts (e.g., dummy data generation)
└── utils/                   # Helper functions and utilities
```

---

## **Key Features**

1. **ETL Pipeline**:

   - Extracts JSON data from MongoDB.
   - Flattens and transforms the data using `pandas.json_normalize`.
   - Loads the transformed data into a MySQL database.

2. **Notification System**:

   - Sends email notifications when an ETL job fails using Airflow's `on_failure_callback`.

3. **Database Model**:

   - A normalized relational database model designed for data integrity and performance.
   - Includes tables for geographical data, orders, addresses, payments, and more.

4. **Query Performance Optimization**:

   - Indexes on frequently queried columns (e.g., `geo_location`, `created_at`).
   - Foreign keys to enforce referential integrity.

5. **Sample Data**:
   - Includes sample JSON data from MongoDB and corresponding flattened CSV data.

---

## **Setup and Installation**

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/YoussefMo7amed/logistics-etl-migration.git
   cd logistics-etl-migration
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Project**:

   - Update the `config/config.json` file with your MongoDB and MySQL connection details.
   - Ensure Airflow is set up if you plan to use the DAG for scheduling.

4. **Set Up the Database**:
   - Run the SQL scripts in `models/sql/sql_models.py` to create the necessary tables in MySQL.

---

## **Running the ETL Pipeline**

1. **Run the Pipeline Locally**:

   ```bash
   python main.py
   ```

2. **Run the Pipeline with Airflow**:
   - Place the `etl_pipeline_dag.py` file in your Airflow `dags` directory.
   - Trigger the DAG from the Airflow UI.

---

## **Database Model**

The database model is designed to ensure data integrity and avoid redundancy. It includes the following tables:

- **Geographical Tables**: `countries`, `cities`, `zones`
- **Address Table**: `addresses`
- **Order-Related Tables**: `orders`, `cod_payments`, `confirmations`, `trackers`
- **Person-Related Tables**: `receivers`, `stars`

For a detailed explanation of the database model, refer to the [data modeling documentation](Docs/data%20modeling.md).

---

## **Sample Data**

- **Source Data**: Sample JSON data from MongoDB is located in `data/source_sample/`.
- **Flattened Data**: Sample flattened data in CSV format is located in `data/output_sample/`.

---

## **Documentation**

- **Challenges**: [challenges.md](Docs/challenges.md)
- **Database Model**: [data modeling.md](Docs/data%20modeling.md)
- **Tasks**: [tasks.md](Docs/tasks.md)

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
