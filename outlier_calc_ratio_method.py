import traceback
import json
import os
import pandas as pd
import boto3


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
            function to calculate ratio.
            :param event: Event object
            :param context: Context object
            :return: JSON string
        """
    # Set up clients
    lambda_client = boto3.client('lambda')

    error_handler_arn = os.environ['error_handler_arn']

    ratio_numerator = os.environ['ratio_numerator']
    ratio_denominator = os.environ['ratio_denominator']
    ratio = os.environ['ratio']

    try:
        input_data = pd.read_json(event)

        ratio_df = calc_ratio(input_data, ratio, ratio_numerator, ratio_denominator)

        json_out = ratio_df.to_json(orient='records')
        final_output = json.loads(json_out)

    except Exception as exc:

        # Invoke error handler lambda
        lambda_client.invoke(
            FunctionName=error_handler_arn,
            InvocationType='Event',
            Payload=json.dumps({'test': 'ccow'})
        )

        return {
            "success": False,
            "error": "Unexpected exception {}".format(_get_traceback(exc))
        }

    return final_output


def calc_ratio(input_table, new_column_name, ratio_numerator, ratio_denominator):
    """
            Generates a DataFrame containing a new column with value of calculated ratios in it.
            :param input_table: DataFrame containing the columns
            :param new_column_name: Column to write the calculated ratio values to
            :param ratio_numerator: Column which provides values for the ratio numerator
            :param ratio_denominator: Column which provides values for the ratio denominator
            :return: DataFrame
            """
    input_table[new_column_name] = (input_table[ratio_numerator] / input_table[ratio_denominator])
    return input_table
