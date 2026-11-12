from unittest.mock import patch

import pandas as pd
import pytest

from genericparser.genericparser import GenericParser


def test_parse_recusa_tipo_de_entrada_desconhecido():
    parser = GenericParser()

    with pytest.raises(Exception, match="Type not accepted by parser"):
        parser.parse(input_value={}, type_input="gitlab")


def test_parse_usa_direto_o_dataframe_devolvido_pelo_plugin():
    df = pd.DataFrame({"a.py": [1.0]}, index=["ncloc"])
    parser = GenericParser()

    with patch.object(GenericParser, "call_plugin", return_value=df) as call_plugin:
        resultado = parser.parse(input_value={"x": 1}, type_input="sonarqube", filters=None)

    call_plugin.assert_called_once_with("genericparser.plugins.statics.sonarqube", {"x": 1}, None)
    assert parser.df is df
    assert resultado == parser.transform_df_to_python_dict(df)
