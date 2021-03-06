import traceback
import json
import os
import boto3
import pandas as pd


def _get_traceback(exception):
    """
    Given an exception, returns the traceback as a string.
    :param exception: Exception object
    :return: string
    """
    return ''.join(
        traceback.format_exception(
            etype=type(exception), value=exception, tb=exception.__traceback__
        )
    )


def lambda_handler(event, context):
    """
        Initialises the environment variables and calls the
        function to carry out aggregation.
        :param event: Event object
        :param context: Context object
        :return: JSON string
    """
    try:
        # Set up clients
        lambda_client = boto3.client('lambda')

        error_handler_arn = os.environ['error_handler_arn']

        aggregate_column = os.environ['aggregate_column']
        sum_aggregate_column = os.environ['sum_aggregate_column']
        strata = os.environ['strata']

        input_data = pd.read_json(event)

        aggregated_df = agg_grouped_data(input_data, aggregate_column, sum_aggregate_column, strata.split())

        json_out = aggregated_df.to_json(orient='records')
        final_output = json.loads(json_out)

    except Exception as exc:

        return {
            "success": False,
            "error": "Unexpected exception {}".format(_get_traceback(exc))
        }

    return final_output


def agg_grouped_data(input_table, target_column, new_column_name, agg_strata):
    """
        Generates an aggregated DataFrame containing a new column
        aggregated(summed) on target_column, grouped on columns provided by agg_strata
        :param input_table: DataFrame containing the columns
        :param target_column: column whose values are to be summed
        :param new_column_name: Column to write the aggregated value to
        :param agg_strata: List of column names to group on
        :return: DataFrame
        """
    input_table[new_column_name] = input_table.groupby(agg_strata)[target_column].transform('sum')
    return input_table
