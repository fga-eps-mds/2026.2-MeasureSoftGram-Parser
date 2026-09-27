from genericparser.genericparser import GenericParser


def test_extract_returns_every_metric_value_for_the_project_component():
    extracted_metrics = GenericParser().parse(
        type_input="sonarqube", input_value="tests/mockfiles/to_extract.json"
    )

    project_key = "fga-eps-mds_2026.2-MeasureSoftGram-Service"
    expected_measures = [
        {"metric": "bugs", "value": "0"},
        {"metric": "code_smells", "value": "72"},
        {"metric": "cognitive_complexity", "value": "598"},
        {"metric": "complexity", "value": "737"},
        {"metric": "coverage", "value": "82.4"},
        {"metric": "duplicated_lines_density", "value": "1.1"},
        {"metric": "files", "value": "109"},
        {"metric": "ncloc", "value": "6227"},
        {"metric": "security_hotspots", "value": "0"},
        {"metric": "sqale_debt_ratio", "value": "0.2"},
        {"metric": "sqale_index", "value": "336"},
        {"metric": "test_errors", "value": "0"},
        {"metric": "test_failures", "value": "0"},
        {"metric": "violations", "value": "98"},
        {"metric": "vulnerabilities", "value": "26"},
    ]

    assert sorted(
        extracted_metrics[project_key], key=lambda measure: measure["metric"]
    ) == sorted(expected_measures, key=lambda measure: measure["metric"])


def test_extract_returns_every_metric_value_for_a_fil_component():
    extracted_metrics = GenericParser().parse(
        type_input="sonarqube", input_value="tests/mockfiles/to_extract.json"
    )

    file_key = (
        "fga-eps-mds_2026.2-MeasureSoftGram-Service:src/organizations/__init__.py"
    )
    expected_measures = [
        {"metric": "complexity", "value": "0"},
        {"metric": "files", "value": "1"},
        {"metric": "ncloc", "value": "0"},
        {"metric": "code_smells", "value": "0"},
        {"metric": "duplicated_lines_density", "value": "0.0"},
        {"metric": "violations", "value": "0"},
        {"metric": "sqale_debt_ratio", "value": "0.0"},
        {"metric": "security_hotspots", "value": "0"},
        {"metric": "sqale_index", "value": "0"},
        {"metric": "bugs", "value": "0"},
        {"metric": "test_failures", "value": "0"},
        {"metric": "cognitive_complexity", "value": "0"},
        {"metric": "vulnerabilities", "value": "0"},
        {"metric": "test_errors", "value": "0"},
    ]

    assert sorted(
        extracted_metrics[file_key], key=lambda measure: measure["metric"]
    ) == sorted(expected_measures, key=lambda measure: measure["metric"])


def test_extract_ignores_components_with_other_qualifiers():
    extracted_metrics = GenericParser().parse(
        type_input="sonarqube", input_value="tests/mockfiles/to_extract.json"
    )

    dir_component_key = "fga-eps-mds_2026.2-MeasureSoftGram-Service:src/accounts"
    assert dir_component_key not in extracted_metrics


def test_extract_does_not_break_when_sqale_debt_ratio_is_missing():
    components_missing_the_metric = [
        {
            "key": "project-missing-metric:src/foo.py",
            "qualifier": "FIL",
            "measures": [
                {"metric": "bugs", "value": "0"},
                {"metric": "coverage", "value": "100.0"},
            ],
        },
    ]

    extracted_metrics = GenericParser().parse(
        type_input="sonarqube",
        input_value=components_missing_the_metric,
    )

    file_key = "project-missing-metric:src/foo.py"

    assert sorted(
        extracted_metrics[file_key], key=lambda measure: measure["metric"]
    ) == sorted(
        [
            {"metric": "bugs", "value": "0"},
            {"metric": "coverage", "value": "100.0"},
        ],
        key=lambda measure: measure["metric"],
    )
