# Table of Contents

1. [Task 1: Data Transformation - Flattening Technique](#task-1-data-transformation---flattening-technique)

   - [Flattening Technique Used](#flattening-technique-used)
   - [Why I Chose This Technique](#why-i-chose-this-technique)
     1. Handles Nested JSON Structures
     2. Flexibility
     3. Ease of Use
     4. Integration with Pandas
     5. Scalability
     6. Customizable Output
   - [Example of Flattening in My Code](#example-of-flattening-in-my-code)
   - [Conclusion](#conclusion)

2. [Task 2: Database Model Design and Justification](#task-2-database-model-design-and-justification)

   - [Objective](#objective)
   - [Database Model Design](#database-model-design)
   - [Key Tables and Relationships](#key-tables-and-relationships)
   - [Justification for Design Choices](#justification-for-design-choices)
   - [Benefits of the Model](#benefits-of-the-model)
   - [Conclusion](#conclusion-1)

3. [Task 3: Enhancing Query Performance](#task-3-enhancing-query-performance)

   - [Objective](#objective-2)
   - [Techniques Used to Optimize Query Performance](#techniques-used-to-optimize-query-performance)
     1. Indexing
     2. Foreign Keys
     3. Enums for Data Consistency
     4. Spatial Data Handling
     5. Timestamp Columns for Auditing
     6. Modular Table Design
   - [Examples of Optimized Queries](#examples-of-optimized-queries)
   - [Conclusion](#conclusion-2)

4. [Task 4: Notification System for Job Failures](#task-4-notification-system-for-job-failures)
   - [Objective](#objective-3)
   - [Implementation of the Notification System](#implementation-of-the-notification-system)
     1. Failure Callback Function
     2. Airflow DAG Configuration
     3. Email Notification Function
     4. Task Definition
     5. Task Dependencies
   - [How the Notification System Works](#how-the-notification-system-works)
     1. Task Failure
     2. Email Notification
     3. Retry Mechanism
   - [Conclusion](#conclusion-3)

### Task 1: Data Transformation - Flattening Technique

#### **Flattening Technique Used**:

In my `transform.py` module, I used **`pandas.json_normalize`** as the primary flattening technique. This function is part of the Pandas library and is specifically designed to take nested JSON structures and flatten them into a tabular format that’s suitable for relational databases.

#### **Why I Chose This Technique**:

1. **Handles Nested JSON Structures**:

   - JSON data often contains nested objects and arrays, which don’t fit neatly into relational database tables. `pandas.json_normalize` automatically flattens these nested structures into a flat table, which makes it much easier to store and query in a relational database.

2. **Flexibility**:

   - The `json_normalize` function allows me to specify exactly which nested fields I want to include in the flattened output using the `meta` parameter. This is super useful when dealing with complex JSON structures, like in the `transform_address_data` function, where I need to extract specific nested fields (e.g., `pickupAddress.floor`, `pickupAddress.firstLine`).

3. **Ease of Use**:

   - Pandas is a library I’m very familiar with, and it’s widely used for data manipulation in Python. The `json_normalize` function is straightforward and doesn’t require me to write custom code for every nested structure, which saves a lot of time.

4. **Integration with Pandas**:

   - Since the rest of my transformation pipeline (like renaming columns, converting data types, etc.) is built using Pandas, using `json_normalize` fits perfectly into the workflow. It keeps everything consistent and easy to manage.

5. **Scalability**:

   - `json_normalize` can handle large datasets efficiently, which is important for ETL processes where performance matters. I don’t have to worry about it breaking down when dealing with a lot of data.

6. **Customizable Output**:
   - The function lets me control the output format, like renaming columns during the flattening process. For example, I rename `_id` to `mongo_id` and nested fields like `firstName` to `first_name` to match SQL naming conventions. This makes the data ready for the database without extra steps.

---

#### **Example of Flattening in My Code**:

In the `transform_address_data` function, I use `json_normalize` to extract nested address fields (e.g., `pickupAddress.floor`, `pickupAddress.firstLine`) and flatten them into a single row per order. Here’s how it works:

```python
df = pd.json_normalize(
    orderCollection,
    record_path=None,
    meta=[
        ["_id"],
        [prefix + "floor"],
        [prefix + "apartment"],
        [prefix + "firstLine"],
        [prefix + "secondLine"],
        [prefix + "district"],
        [prefix + "geoLocation"],
        [prefix + "zone"],
        [prefix + "city"],
        [prefix + "country"],
        "createdAt",
        "updatedAt",
    ],
)
```

- **`meta` Parameter**: This lets me specify which nested fields to include in the flattened output.
- **`record_path` Parameter**: This is used to extract arrays of nested objects, but I didn’t need it here since I was focusing on flattening nested fields within each order.

#### **Conclusion**:

I chose `pandas.json_normalize` as my flattening technique because it’s robust, flexible, and efficient. It handles nested JSON data seamlessly and integrates perfectly with the rest of my transformation pipeline. This approach aligns with the goal of transforming unstructured JSON data into a structured format for relational databases, and it ensures that the ETL process is scalable, maintainable, and easy to work with.

---

### **Task 2: Database Model Design and Justification**

#### **Objective**:

The goal of this task was to design a normalized database model that ensures **data integrity** and **avoids redundancy** while maintaining clear and maintainable relationships between tables. Below, I explain the design choices and justify why this model is effective for the given requirements.

---

#### **Database Model Design**

The database model is designed to be **normalized to at least Third Normal Form (3NF)**, ensuring that:

1. **Data is organized into logical tables** (e.g., `countries`, `cities`, `zones`, `addresses`, `orders`, etc.).
2. **Redundancy is minimized** by separating entities into distinct tables and using foreign keys to establish relationships.
3. **Dependencies are properly managed** (e.g., `addresses` depend on `zones`, `cities`, and `countries`).

_For more details, please refer to the [data modeling.md](./data%20modeling.md) file_

---

#### **Key Tables and Relationships**

1. **Geographical Tables (`countries`, `cities`, `zones`)**:

   - These tables store hierarchical geographical data, ensuring that each entity (e.g., a city or zone) is stored only once.
   - **Foreign Keys**: The `addresses` table references `zones`, `cities`, and `countries`, ensuring that addresses are always linked to valid geographical entities.

2. **`addresses` Table**:

   - This table stores both pickup and drop-off addresses, with a `type` column to distinguish between them.
   - **Foreign Keys**: It references `zones`, `cities`, and `countries`, ensuring that addresses are always associated with valid geographical data.
   - **Indexes**: The `idx_order_mongo_address_type` index ensures that each order has only one pickup and one drop-off address, preventing duplicates.

3. **`orders` Table**:

   - This is the central table that ties everything together. It references `addresses` (for pickup and drop-off locations), `receivers`, and `stars`.
   - **Foreign Keys**: `pickup_address_id`, `dropoff_address_id`, `receiver_id`, and `star_id` ensure that orders are linked to valid addresses, receivers, and stars.
   - **Indexes**: Multiple indexes (e.g., `idx_orders_receiver_id`, `idx_orders_pickup_address_id`) optimize query performance for common lookups.

4. **`receivers` and `stars` Tables**:

   - These tables store information about the people involved in the orders (receivers and stars). They are separate to avoid redundancy and ensure that each entity is stored only once.

5. **`cod_payments` and `confirmations` Tables**:

   - These tables store payment and confirmation details related to orders. They are separate to maintain a clear separation of concerns and avoid bloating the `orders` table.
   - **Foreign Keys**: Both tables reference `orders`, ensuring that payments and confirmations are always linked to valid orders.

6. **`trackers` Table**:
   - This table tracks order progress and is linked to the `orders` table via a foreign key. It ensures that tracking information is stored separately but remains connected to the relevant order.

---

#### **Justification for Design Choices**

1. **Normalization**:

   - The model is normalized to **Third Normal Form (3NF)**, which eliminates redundancy and ensures data integrity. For example, geographical data (e.g., cities, zones) is stored only once and reused across the application.

2. **Foreign Keys and Relationships**:

   - Foreign keys (e.g., `zone_id`, `city_id`, `country_id` in `addresses`) enforce referential integrity, preventing orphaned records and ensuring that relationships between tables are always valid.

3. **Indexes for Performance**:

   - Indexes like `idx_addresses_geo` (for geolocation) and `idx_orders_created_at` (for timestamp-based queries) improve query performance, especially for large datasets.
   - Unique indexes (e.g., `idx_order_mongo_address_type`) enforce data integrity by preventing duplicate entries.

4. **Use of Enums and Constraints**:

   - Enums (e.g., `type` in `orders` and `addresses`) restrict values to predefined options, ensuring data consistency.
   - Constraints (e.g., `NOT NULL`, `UNIQUE`) ensure that required fields are always populated and that unique values are enforced.

5. **Timestamps for Auditing**:

   - The `created_at` and `updated_at` columns in almost every table provide a clear audit trail, making it easy to track when records were created or modified.

6. **Spatial Data Handling**:

   - The `geo_location` column in the `addresses` table uses the `Geometry` type (from `geoalchemy2`) to store geolocation data as points. This allows for spatial queries, such as finding addresses within a certain radius.

7. **Scalability and Maintainability**:
   - The modular design allows for easy extension or modification. For example, adding a new entity (e.g., a new type of payment) would only require creating a new table without disrupting existing ones.
   - Reusable tables (e.g., `countries`, `cities`, `zones`) reduce redundancy and improve maintainability.

---

#### **Benefits of the Model**

1. **Data Integrity**:

   - Foreign keys, unique constraints, and enums ensure that the data remains consistent and valid.

2. **Avoids Redundancy**:

   - By separating entities into distinct tables, the model minimizes duplication (e.g., storing city names only once in the `cities` table).

3. **Scalability**:

   - The modular design allows for easy expansion as new requirements arise.

4. **Performance**:

   - Indexes and well-defined relationships optimize query performance, even for large datasets.

5. **Auditability**:
   - Timestamps and clear relationships make it easy to track changes and debug issues.

---

#### **Conclusion**

The database model is designed to be **normalized, scalable, and maintainable**, with a strong focus on **data integrity** and **performance**. By organizing data into logical tables, using foreign keys to enforce relationships, and leveraging indexes for optimization, the model effectively avoids redundancy and ensures that the data remains consistent and easy to query. This design provides a solid foundation for handling complex data relationships in a relational database.

---

### **Task 3: Enhancing Query Performance**

#### **Objective**:

The goal of this task is to optimize query performance for the database. Below, I outline the techniques used to enhance query performance in the database model and provide specific examples from the design.

---

#### **Techniques Used to Optimize Query Performance**

1. **Indexing**:

   - **Purpose**: Indexes are used to speed up data retrieval operations by allowing the database to quickly locate rows without scanning the entire table.
   - **Implementation**:
     - **Geolocation Index**: The `idx_addresses_geo` index on the `geo_location` column in the `addresses` table optimizes spatial queries, such as finding addresses within a certain radius.
     - **Order-Related Indexes**: Indexes like `idx_orders_receiver_id`, `idx_orders_pickup_address_id`, and `idx_orders_dropoff_address_id` in the `orders` table speed up lookups based on these frequently queried columns.
     - **Timestamp Indexes**: Indexes like `idx_orders_created_at` and `idx_orders_updated_at` optimize queries that filter or sort by creation or update times.
     - **Unique Indexes**: The `idx_order_mongo_address_type` index in the `addresses` table ensures that each order has only one pickup and one drop-off address, while also speeding up lookups based on `order_mongo_id` and `type`.

2. **Foreign Keys**:

   - **Purpose**: Foreign keys enforce referential integrity and improve query performance by enabling efficient joins between related tables.
   - **Implementation**:
     - Foreign keys like `zone_id`, `city_id`, and `country_id` in the `addresses` table allow for fast joins with the `zones`, `cities`, and `countries` tables.
     - Foreign keys like `pickup_address_id`, `dropoff_address_id`, `receiver_id`, and `star_id` in the `orders` table optimize queries involving order-related data.

3. **Enums for Data Consistency**:

   - **Purpose**: Enums restrict column values to predefined options, reducing the need for complex validation logic and improving query performance by limiting the range of possible values.
   - **Implementation**:
     - The `type` column in the `orders` table uses an enum (`SEND`, `RECEIVE`) to ensure consistency and speed up queries filtering by order type.
     - The `type` column in the `addresses` table uses an enum (`pickup`, `dropoff`) to distinguish between address types efficiently.

4. **Spatial Data Handling**:

   - **Purpose**: Efficiently storing and querying geolocation data.
   - **Implementation**:
     - The `geo_location` column in the `addresses` table uses the `Geometry` type (from `geoalchemy2`) to store points. This allows for optimized spatial queries, such as finding addresses within a specific area.

5. **Timestamp Columns for Auditing**:

   - **Purpose**: Timestamps like `created_at` and `updated_at` help track changes and optimize time-based queries.
   - **Implementation**:
     - Indexes on `created_at` and `updated_at` columns (e.g., `idx_orders_created_at`) speed up queries that filter or sort by these timestamps.

6. **Modular Table Design**:
   - **Purpose**: Separating data into logical tables reduces redundancy and improves query performance by minimizing the amount of data scanned during queries.
   - **Implementation**:
     - Tables like `cod_payments` and `confirmations` are separate from the `orders` table, ensuring that queries on payment or confirmation data do not need to scan the entire `orders` table.

---

#### **Examples of Optimized Queries**

1. **Finding Orders by Receiver**:

   - **Query**: Retrieve all orders for a specific receiver.
   - **Optimization**: The `idx_orders_receiver_id` index on the `receiver_id` column in the `orders` table speeds up this query.

2. **Spatial Query for Addresses**:

   - **Query**: Find all addresses within a 10 km radius of a given point.
   - **Optimization**: The `idx_addresses_geo` index on the `geo_location` column optimizes this spatial query.

3. **Filtering Orders by Type**:

   - **Query**: Retrieve all orders of type `SEND`.
   - **Optimization**: The `idx_orders_type` index on the `type` column in the `orders` table speeds up this query.

4. **Time-Based Queries**:
   - **Query**: Retrieve all orders created in the last 7 days.
   - **Optimization**: The `idx_orders_created_at` index on the `created_at` column optimizes this query.

---

#### **Conclusion**

The database model incorporates several techniques to enhance query performance, including **indexing**, **foreign keys**, **enums**, **spatial data handling**, and **modular table design**. These optimizations ensure that the database can handle complex queries efficiently, even as the dataset grows. By carefully designing indexes and relationships, the model achieves a balance between performance and maintainability, making it well-suited for real-world applications.

---

### **Task 4: Notification System for Job Failures**

#### **Objective**:

The goal of this task is to implement a notification system that alerts stakeholders when an ETL job fails. This ensures that issues are promptly identified and addressed, minimizing downtime and data pipeline disruptions.

---

#### **Implementation of the Notification System**

The notification system is implemented in the `etl_pipeline_dag.py` file using **Apache Airflow**, a popular workflow orchestration tool. Below is a detailed explanation of how the notification system works:

1. **Failure Callback Function**:

   - A function named `send_failure_notification` is defined to handle job failures. This function is triggered whenever a task in the DAG fails.
   - The function calls `send_failure_email(context)`, which is responsible for sending an email notification with details about the failure.

   ```python
   def send_failure_notification(context):
       send_failure_email(context)
   ```

2. **Airflow DAG Configuration**:

   - The DAG is configured with a `default_args` dictionary, which includes the `on_failure_callback` parameter. This parameter specifies the `send_failure_notification` function to be called when a task fails.
   - Other parameters like `retries` and `start_date` are also configured to control the behavior of the DAG.

   ```python
   default_args = {
       "owner": "airflow",
       "depends_on_past": False,
       "start_date": datetime.today(),
       "retries": 3,
       "on_failure_callback": send_failure_notification,
   }
   ```

3. **Email Notification Function**:

   - The `send_failure_email` function (imported from `utils.helpers`) is responsible for sending email notifications. It uses the `context` parameter, which contains details about the failed task, such as the task ID, execution date, and error message.
   - This function can be customized to include relevant information in the email, such as the task name, error logs, and links to the Airflow UI for further investigation.

4. **Task Definition**:

   - The DAG consists of three tasks (`first_pipeline_task`, `second_pipeline_task`, `third_pipeline_task`), each representing a stage in the ETL pipeline.
   - If any of these tasks fail, the `on_failure_callback` is triggered, and an email notification is sent.

   ```python
   first_pipeline_task = PythonOperator(
       task_id="first_pipeline",
       python_callable=first_pipeline,
       dag=dag,
   )

   second_pipeline_task = PythonOperator(
       task_id="second_pipeline",
       python_callable=second_pipeline,
       dag=dag,
   )

   third_pipeline_task = PythonOperator(
       task_id="third_pipeline",
       python_callable=third_pipeline,
       dag=dag,
   )
   ```

5. **Task Dependencies**:

   - The tasks are executed in a specific order: `first_pipeline_task` → `second_pipeline_task` → `third_pipeline_task`.
   - If any task fails, the subsequent tasks are not executed, and the failure notification is sent immediately.

   ```python
   first_pipeline_task >> second_pipeline_task >> third_pipeline_task
   ```

---

#### **How the Notification System Works**

1. **Task Failure**:

   - If a task (e.g., `first_pipeline_task`) fails, Airflow triggers the `on_failure_callback` function (`send_failure_notification`).

2. **Email Notification**:

   - The `send_failure_notification` function calls `send_failure_email(context)`, which sends an email to the configured recipients.
   - The email includes details about the failed task, such as:
     - Task ID
     - Execution date
     - Error message or logs
     - Links to the Airflow UI for further investigation.

3. **Retry Mechanism**:
   - The `retries` parameter in `default_args` ensures that the task is retried up to 3 times before marking it as failed. If all retries fail, the notification is sent.

---

#### **Conclusion**

The notification system implemented in the `etl_pipeline_dag.py` file ensures that stakeholders are promptly alerted when an ETL job fails. By using Airflow's `on_failure_callback` mechanism and a custom email notification function, the system provides a robust and scalable solution for monitoring and addressing pipeline failures. This proactive approach minimizes downtime and ensures the reliability of the ETL process.
