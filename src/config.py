# pylint: disable=no-self-argument
# pylint: disable=line-too-long
"""
Module: config

This module provides utilities to handle and validate report configuration data using Pydantic models and SQL queries.

Classes:
- ReportPageConfig: Pydantic model for a report configuration with validation methods for measureId.
- BaseModel: Pydantic's BaseModel for defining data models.

Functions:
- validate_config: Validates a list of configurations and returns a list of ReportPageConfig instances.
- load_report_config: Loads report configurations from a JSON file, validates them, and returns a list of ReportPageConfig instances.
"""
from typing import Optional, List, Dict, Any
import re
import json
from pydantic import BaseModel, field_validator


PRINT_MEASURES_TABLE = "scd.Measure_Print"


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

    # @field_validator("measureId")
    # def validate_measure_exists(cls, value: str) -> str:
    #     """
    #     Validator for measureId existence in the database table.

    #     Args:
    #     - value (str): Value of the measureId to validate.

    #     Returns:
    #     - str: The validated measureId value.

    #     Raises
    #     - ValueError: If measureId specified does not exist in the config table.
    #     """
    #     pass
    #     # if value:
    #     #     page = read_sql(
    #     #         f"SELECT measure_id FROM {PRINT_MEASURES_TABLE} WHERE measure_id = '{value}'"
    #     #     )
    #     #     if page.empty:
    #     #         raise ValueError(
    #     #             "measureId specified does not exist in the config table"
    #     #         )
    #     # return value


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


def load_report_config(config_path: str) -> List[ReportPageConfig]:
    """
    Loads report configurations from a JSON file, validates them, and returns a list of ReportPageConfig instances.

    Args:
    - config_path (str): Path to the JSON file containing report configurations.

    Returns:
    - List[ReportPageConfig]: A list of validated ReportPageConfig instances.
    """
    with open(config_path, encoding="utf-8") as file:
        j = json.load(file)

    config = validate_config(j)
    return config
