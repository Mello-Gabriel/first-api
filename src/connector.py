"""BigQuery Connector for data operations."""

from google.cloud import bigquery
from google.api_core import exceptions
import pandas as pd
import os


class BigQueryConnector:
    """
    A connector class for interacting with Google BigQuery.

    This class provides methods to execute SQL queries, retrieve data as pandas DataFrames,
    and upload data to BigQuery tables.
    """

    def __init__(self, project_id, credentials_path=None):
        """
        Initializes the BigQueryConnector.

        Args:
        project_id (str): The Google Cloud project ID where the BigQuery dataset and table reside.
        credentials_path (str, optional): The absolute path to the service account JSON key file.
        """
        # --- FIX START ---
        # Set the environment variable BEFORE initializing the client.
        # This ensures the client knows how to authenticate right away.
        if credentials_path:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credential file not found at: {credentials_path}"
                )
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Now, initialize the client. It will automatically use the credentials
        # from the environment variable. Passing the project_id here is good practice.
        self.client = bigquery.Client(project=project_id)
        # --- FIX END ---

    def query(self, sql_query):
        """
        Executes a SQL query on BigQuery and returns the results.

        Args:
        sql_query (str): The SQL query string to execute.

        Returns:
        google.cloud.bigquery.table._RowIterator: An iterator over the query results.
        """
        try:
            query_job = self.client.query(sql_query)  # API request
            return query_job.result()  # Waits for query to finish and returns iterator
        except exceptions.GoogleAPICallError as e:
            # Catch specific API errors for better logging
            print(f"An API error occurred during query execution: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during query execution: {e}")
            raise

    def query_to_df(self, sql_query):
        """
        Executes a SQL query and returns the results as a pandas DataFrame.

        Args:
        sql_query (str): The SQL query string to execute.

        Returns:
        pandas.DataFrame: A pandas DataFrame containing the query results.
        """
        try:
            # The to_dataframe() method handles the query execution and result fetching.
            return self.client.query(sql_query).to_dataframe()
        except exceptions.GoogleAPICallError as e:
            print(f"An API error occurred while fetching data as DataFrame: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred while fetching data as DataFrame: {e}")
            raise

    def upload_data(self, dataset_id, table_id, data):
        """
        Uploads data to a specified BigQuery table.

        This method supports uploading data from a pandas DataFrame.
        It appends the data to the existing table if the table already exists.

        Args:
        dataset_id (str): The ID of the BigQuery dataset.
        table_id (str): The ID of the BigQuery table.
        data (pandas.DataFrame): The data to upload. Currently only supports pandas DataFrames.

        Raises:
        TypeError: If the input `data` is not a pandas DataFrame.
        """
        try:
            if not isinstance(data, pd.DataFrame):
                raise TypeError("Input data must be a pandas DataFrame.")

            table_ref = self.client.dataset(dataset_id).table(table_id)
            job_config = bigquery.LoadJobConfig()
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

            # Correctly call load_table_from_dataframe
            job = self.client.load_table_from_dataframe(
                data, table_ref, job_config=job_config
            )
            job.result()  # Waits for the job to complete.
            print(f"Loaded {job.output_rows} rows into {dataset_id}.{table_id}")

        except Exception as e:
            print(
                f"An error occurred during data upload to {dataset_id}.{table_id}: {e}"
            )
            raise
