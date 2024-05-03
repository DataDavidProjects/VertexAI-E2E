from dataclasses import dataclass
import pandas as pd
from google.cloud import bigquery
from typing import List
from pathlib import Path
from google.cloud.bigquery.job import LoadJobConfig, WriteDisposition
from jinja2 import Template  # pylint: disable=E0401


def generate_query(input_file: Path, **replacements) -> str:
    """
    Read input file and replace placeholder using Jinja.

    Args:
        input_file (Path): input file to read
        replacements: keyword arguments to use to replace placeholders
    Returns:
        str: replaced content of input file
    """

    with open(input_file, "r", encoding="utf-8") as f:
        query_template = f.read()

    return Template(query_template).render(**replacements)


@dataclass
class TableConfig:
    """
    Configuration for creating a BigQuery table.

    Args:
        dataset_id (str): The ID of the dataset in BigQuery.
        table_id (str): The ID of the table in BigQuery.
        schema (List[bigquery.SchemaField], optional): The schema of the table. Defaults to None.
        df (pd.DataFrame, optional): The pandas DataFrame to create the table from. Defaults to None.
        partitioning_field (str, optional): The field to partition the table on. Defaults to None.
        partitioning_type (str, optional): The type of partitioning. Defaults to 'DAY'.
        partitioning_field_type (str, optional): The type of the partitioning field. Defaults to 'DATE'.
    """

    dataset_id: str
    table_id: str
    schema: List[bigquery.SchemaField] = None
    partitioning_field: str = None
    partitioning_type: str = "DAY"
    partitioning_field_type: str = "DATE"


@dataclass
class ExternalTableConfig:
    """
    Configuration for creating an external BigQuery table.

    Args:
        dataset_id (str): The ID of the dataset in BigQuery.
        table_id (str): The ID of the table in BigQuery.
        data_uri (str): The URI of the data in Google Cloud Storage.
        schema (List[bigquery.SchemaField]): The schema of the table.
        format (str, optional): The format of the data. Defaults to 'CSV'.
        skip_leading_rows (int, optional): The number of leading rows to skip. Defaults to 1.
    """

    dataset_id: str
    table_id: str
    data_uri: str
    schema: List[bigquery.SchemaField]
    format: str = "CSV"
    skip_leading_rows: int = 1


@dataclass
class BigQueryConf:
    """
    Configuration for BigQuery operations.

    Args:
        client (bigquery.Client): The BigQuery client.
    """

    client: bigquery.Client = bigquery.Client()

    def create_dataset(self, dataset_id: str) -> bigquery.Dataset:
        """
        Create a BigQuery dataset.

        Args:
            dataset_id (str): The ID of the dataset to create.

        Returns:
            bigquery.Dataset: The created dataset.
        """
        dataset_ref = self.client.dataset(dataset_id)
        dataset = bigquery.Dataset(dataset_ref)
        dataset = self.client.create_dataset(dataset)  # API request
        print(f"Created dataset {dataset.project}.{dataset.dataset_id}")
        return dataset

    def create_table(self, config: TableConfig) -> bigquery.Table:
        """
        Create a table in BigQuery.

        Args:
            config (TableConfig): The configuration for the table.

        Returns:
            bigquery.Table: The created table.
        """
        table_ref = self.client.dataset(config.dataset_id).table(config.table_id)
        table = bigquery.Table(table_ref, schema=config.schema)
        if config.partitioning_field:
            table.time_partitioning = bigquery.TimePartitioning(
                type_=config.partitioning_type,
                field=config.partitioning_field,
                require_partition_filter=True,
            )
        table = self.client.create_table(table)
        return table

    def create_table_from_pandas(
        self, df: pd.DataFrame, config: TableConfig
    ) -> bigquery.Table:
        """
        Create a table in BigQuery from a pandas DataFrame.

        Args:
            df (pd.DataFrame): The pandas DataFrame to create the table from.
            config (TableConfig): The configuration for the table.

        Returns:
            bigquery.Table: The created table.
        """
        if config.schema is None:
            pandas_dtype_to_bigquery_dtype = {
                "int64": "INT64",
                "float64": "FLOAT64",
                "bool": "BOOL",
                "datetime64[ns]": "TIMESTAMP",
                "object": "STRING",
            }
            config.schema = [
                bigquery.SchemaField(
                    name, pandas_dtype_to_bigquery_dtype[str(df[name].dtype)]
                )
                for name in df.columns
            ]
        table = self.create_table(config)
        job_config = bigquery.LoadJobConfig(schema=config.schema)
        job = self.client.load_table_from_dataframe(df, table, job_config=job_config)
        job.result()  # Wait for the job to complete
        return table

    def create_external_table(self, config: ExternalTableConfig) -> bigquery.Table:
        """
        Create an external table in BigQuery that references data in Google Cloud Storage.

        Args:
            config (ExternalTableConfig): The configuration for the external table.

        Returns:
            bigquery.Table: The created table.
        """
        # Construct a BigQuery table reference
        table_ref = self.client.dataset(config.dataset_id).table(config.table_id)
        # Create the external config
        external_config = bigquery.ExternalConfig(config.format)
        external_config.source_uris = [config.data_uri]
        external_config.schema = config.schema
        external_config.options.skip_leading_rows = config.skip_leading_rows
        # Create the table
        table = bigquery.Table(table_ref, schema=config.schema)
        table.external_data_configuration = external_config
        table = self.client.create_table(table)  # API request
        print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
        return table

    def extend_table(self, df: pd.DataFrame, config: TableConfig) -> bigquery.Table:
        """
        Append rows to an existing table in BigQuery from a pandas DataFrame.

        Args:
            df (pd.DataFrame): The pandas DataFrame to append to the table.
            config (TableConfig): The configuration for the table.

        Returns:
            bigquery.Table: The updated table.
        """
        table_ref = self.client.dataset(config.dataset_id).table(config.table_id)
        job_config = LoadJobConfig(
            schema=config.schema,
            write_disposition=WriteDisposition.WRITE_APPEND,
        )
        job = self.client.load_table_from_dataframe(
            df, table_ref, job_config=job_config
        )
        job.result()  # Wait for the job to complete
        table = self.client.get_table(table_ref)  # Get the updated table
        return table

    def delete_table(self, config: TableConfig) -> None:
        """
        Delete a table in BigQuery.

        Args:
            config (TableConfig): The configuration for the table.
        """
        table_ref = self.client.dataset(config.dataset_id).table(config.table_id)
        self.client.delete_table(table_ref)

    def delete_dataset(self, dataset_id: str) -> None:
        """
        Delete a dataset in BigQuery.

        Args:
            dataset_id (str): The ID of the dataset.
        """
        dataset_ref = self.client.dataset(dataset_id)
        self.client.delete_dataset(dataset_ref, delete_contents=True, not_found_ok=True)
