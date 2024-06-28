# pylint: disable=no-self-argument
# pylint: disable=line-too-long
"""
Module: config

This module provides utilities to handle and validate report configuration data using Pydantic models and SQL queries.

Classes:
- ReportPageConfig: Pydantic model for a report configuration with validation methods for measureId.

Functions:
- get_page_config: Retrieves the configuration for a given page name from the database.
- validate_config: Validates a list of configurations and returns a list of ReportPageConfig instances.
- load_report_config: Loads report configurations for a given page name, validates them, and returns a list of ReportPageConfig instances.
"""
from typing import Optional, List, Dict, Any
import re
from pydantic import BaseModel, field_validator
from sql import read_sql

PRINT_MEASURES_TABLE = "scd.MeasurePrint_Dynamic"


class ReportPageConfig(BaseModel):
    """
    Pydantic model for a report configuration.

    Attributes:
    - pageName (str): Name of the page.
    - displayName (str): Display name of the page.
    - pageOrder (int): Order of the page.
    - measureId (Optional[str]): Optional identifier for the measure.

    Validators:
    - validate_measure: Validates the measureId format.
    - validate_measure_exists: Validates if the measureId exists in the database table.
    """

    pageName: str
    displayName: str
    pageOrder: int
    measureId: Optional[str]
    comparativeMeasureId: Optional[str]

    @field_validator("measureId")
    def validate_measure(cls, value: str) -> str:
        """
        Validator for measureId format.

        Args:
        - value (str): Value of the measureId to validate.

        Returns:
        - str: The validated measureId value.

        Raises:
        - ValueError: If measureId does not match the format "BR{3 digits int}".
        """
        if value:
            if not re.match(r"^BR\d{3}$", value):
                raise ValueError('measureId must match the format "BR{3 digits int}"')
        return value


def get_page_config(page_name: str) -> List[Dict[str, Any]]:
    """
    Retrieves the configuration for a given page name from the database.

    Args:
    - page_name (str): The name of the page.

    Returns:
    - List[Dict[str, Any]]: A list of dictionaries representing configurations.

    Raises:
    - ValueError: If no configuration is found for the given page name.
    """
    if page_name == "Full Report":
        config_query = f"""SELECT name as pageName,
        displayName,
        rowid as pageOrder,
        measure_id as measureId,
        comparative_measure_id as comparativeMeasureId
        FROM
        {PRINT_MEASURES_TABLE}"""
    else:
        config_query = f"""SELECT name as pageName,
        displayName,
        rowid as pageOrder,
        measure_id as measureId,
        comparative_measure_id as comparativeMeasureId
        FROM
        {PRINT_MEASURES_TABLE}
        WHERE
        displayName = '{page_name}'"""
    config = read_sql(config_query)
    if config.empty:
        raise ValueError("Specified page does not exist")
    config = config.to_dict(orient="records")
    return config


def validate_config(config_list: List[Dict[str, Any]]) -> List[ReportPageConfig]:
    """
    Validates a list of configurations and returns a list of ReportPageConfig instances.

    Args:
    - config_list (List[Dict[str, Union[str, int, None]]]): A list of dictionaries representing configurations.

    Returns:
    - List[ReportPageConfig]: A list of validated ReportPageConfig instances.
    """
    validated_configs = []
    for config_dict in config_list:
        conf = ReportPageConfig(
            pageName=config_dict["pageName"],
            displayName=config_dict["displayName"],
            pageOrder=config_dict["pageOrder"],
            measureId=config_dict["measureId"],
            comparativeMeasureId=config_dict["comparativeMeasureId"],
        )

        validated_configs.append(conf)

    return validated_configs


def load_report_config(page_name: str) -> List[ReportPageConfig]:
    """
    Loads report configurations from a JSON file, validates them, and returns a list of ReportPageConfig instances.

    Args:
        measure_name (str): The name of the measure whose configuration is to be loaded.

    Returns:
        List[ReportPageConfig]: A list of validated ReportPageConfig instances.

    Raises:
        ValueError: If no configuration is found for the given measure name.
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the JSON file cannot be decoded.
    """
    config_data = get_page_config(page_name)
    config = validate_config(config_data)
    return config
