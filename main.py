from scripts import create_dummy_data
from etl.etl_pipeline import run_pipeline

if __name__ == "__main__":
    # Generate dummy data for testing
    create_dummy_data()
    # Run the ETL pipeline
    run_pipeline()
