from genericparser.genericparser import GenericParser
from tests.mockfiles.mock_input_pandas_transform import dataframe_input
from tests.mockfiles.mock_output_pandas_transform import dict_output


def test_df_to_dict_test():
    assert GenericParser().transform_df_to_python_dict(dataframe_input) == dict_output


def test_parse_builds_the_dict_consumed_by_the_service_with_security_metrics():
    """Caminho completo do parse com as metricas de seguranca: componente do
    projeto e arquivos, cada um com as suas metricas tipadas."""
    components = [
        {
            "key": "project",
            "qualifier": "TRK",
            "measures": [
                {"metric": "security_rating", "value": "2.0"},
                {"metric": "security_review_rating", "value": "3.0"},
                {"metric": "vulnerabilities", "value": "26"},
                {"metric": "ncloc", "value": "6227"},
            ],
        },
        {
            "key": "project:src/foo.py",
            "qualifier": "FIL",
            "measures": [
                {"metric": "security_rating", "value": "1.0"},
                {"metric": "vulnerabilities", "value": "0"},
                {"metric": "ncloc", "value": "1200"},
            ],
        },
    ]

    parsed = GenericParser().parse(type_input="sonarqube", input_value=components)

    assert parsed == {
        "project": [
            {"metric": "ncloc", "value": 6227.0},
            {"metric": "security_rating", "value": 2.0},
            {"metric": "security_review_rating", "value": 3.0},
            {"metric": "vulnerabilities", "value": 26.0},
        ],
        "project:src/foo.py": [
            {"metric": "ncloc", "value": 1200.0},
            {"metric": "security_rating", "value": 1.0},
            {"metric": "vulnerabilities", "value": 0.0},
        ],
    }


def test_parse_keeps_other_metrics_when_a_security_metric_is_missing():
    """Metrica de seguranca ausente em um dos arquivos nao derruba o parse nem
    contamina os outros componentes: so a medida dependente fica sem dado."""
    components = [
        {
            "key": "project:src/com_rating.py",
            "qualifier": "FIL",
            "measures": [
                {"metric": "security_rating", "value": "1.0"},
                {"metric": "coverage", "value": "90.0"},
            ],
        },
        {
            "key": "project:src/sem_rating.py",
            "qualifier": "FIL",
            "measures": [
                {"metric": "coverage", "value": "80.0"},
            ],
        },
    ]

    parsed = GenericParser().parse(type_input="sonarqube", input_value=components)

    assert parsed["project:src/com_rating.py"] == [
        {"metric": "coverage", "value": 90.0},
        {"metric": "security_rating", "value": 1.0},
    ]
    assert parsed["project:src/sem_rating.py"] == [
        {"metric": "coverage", "value": 80.0},
    ]
