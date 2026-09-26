import json

from genericparser.genericparser import GenericParser


def test_extract_sonarqube_available_metrics():
    extracted_metrics = GenericParser().parse(
        type_input="sonarqube", input_value="tests/mockfiles/to_extract.json"
    )

    with open("tests/mockfiles/extracted.json", "r") as f:
        assert set(extracted_metrics.keys()).issubset(json.loads(f.read()).keys())
