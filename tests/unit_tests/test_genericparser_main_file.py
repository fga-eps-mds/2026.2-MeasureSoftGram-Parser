from genericparser.genericparser import GenericParser
from tests.mockfiles.mock_input_pandas_transform import dataframe_input
from tests.mockfiles.mock_output_pandas_transform import dict_output


def test_df_to_dict_test():
    assert GenericParser().transform_df_to_python_dict(dataframe_input) == dict_output
