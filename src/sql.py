"""
This module provides a utility for connecting to a SQL Server database using SQLAlchemy
and executing SQL queries to return the results as a Pandas DataFrame. It uses context managers
for managing the database connection and dotenv for loading environment variables.

Functions:
- connection: A context manager for creating and closing the database connection.
- read_sql: Executes a SQL query and returns the result as a Pandas DataFrame.
"""

from contextlib import contextmanager
import urllib
from typing import Iterator
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from utils import get_credential  # pylint: disable=import-error


@contextmanager
def connection() -> Iterator[Engine]:
    """
    Context manager to create and close a database connection.

    Loads database connection parameters from environment variables, creates
    a SQLAlchemy engine, and yields the engine. The engine is closed when the
    context is exited.

    Returns:
        Iterator[Engine]: An iterator that yields a SQLAlchemy Engine.
    """

    connstr = get_credential("public-dataflow-connectionstring")
    params = urllib.parse.quote_plus(connstr)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    try:
        yield engine
    finally:
        engine.dispose()


def read_sql(query: str) -> pd.DataFrame:
    """
    Executes a SQL query and returns the result as a Pandas DataFrame.

    Args:
        query (str): The SQL query to execute.

    Returns:
        pd.DataFrame: A DataFrame containing the query results.
    """
    with connection() as conn:
        return pd.read_sql(sql=query, con=conn)
