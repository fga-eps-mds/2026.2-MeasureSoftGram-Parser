from genericparser.genericparser import GenericParser


def test_extract_returns_every_metric_value_for_the_project_component():
    extracted_metrics = GenericParser().parse(
        type_input="sonarqube", input_value="tests/mockfiles/to_extract.json"
    )

    project_key = "fga-eps-mds_2026.2-MeasureSoftGram-Service"
    expected_measures = [
        {"metric": "bugs", "value": 0.0},
        {"metric": "code_smells", "value": 72.0},
        {"metric": "cognitive_complexity", "value": 598.0},
        {"metric": "complexity", "value": 737.0},
        {"metric": "coverage", "value": 82.4},
        {"metric": "duplicated_lines_density", "value": 1.1},
        {"metric": "files", "value": 109.0},
        {"metric": "ncloc", "value": 6227.0},
        {"metric": "security_hotspots", "value": 0.0},
        {"metric": "sqale_debt_ratio", "value": 0.2},
        {"metric": "sqale_index", "value": 336.0},
        {"metric": "test_errors", "value": 0.0},
        {"metric": "test_failures", "value": 0.0},
        {"metric": "violations", "value": 98.0},
        {"metric": "vulnerabilities", "value": 26.0},
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
        {"metric": "complexity", "value": 0.0},
        {"metric": "files", "value": 1.0},
        {"metric": "ncloc", "value": 0.0},
        {"metric": "code_smells", "value": 0.0},
        {"metric": "duplicated_lines_density", "value": 0.0},
        {"metric": "violations", "value": 0.0},
        {"metric": "sqale_debt_ratio", "value": 0.0},
        {"metric": "security_hotspots", "value": 0.0},
        {"metric": "sqale_index", "value": 0.0},
        {"metric": "bugs", "value": 0.0},
        {"metric": "test_failures", "value": 0.0},
        {"metric": "cognitive_complexity", "value": 0.0},
        {"metric": "vulnerabilities", "value": 0.0},
        {"metric": "test_errors", "value": 0.0},
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
                {"metric": "bugs", "value": 0.0},
                {"metric": "coverage", "value": 100.0},
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
            {"metric": "bugs", "value": 0.0},
            {"metric": "coverage", "value": 100.0},
        ],
        key=lambda measure: measure["metric"],
    )


SECURITY_METRICS = [
    "security_rating",
    "vulnerabilities",
    "security_hotspots",
    "security_review_rating",
]


def _component(key, qualifier, measures):
    return {"key": key, "qualifier": qualifier, "measures": measures}


def test_extract_types_security_metrics_as_numbers():
    """As medidas de seguranca do Core consomem valor numerico; o SonarQube
    entrega string, e a conversao e responsabilidade da extracao."""
    components = [
        _component(
            "project:src/foo.py",
            "FIL",
            [
                {"metric": "security_rating", "value": "1.0"},
                {"metric": "vulnerabilities", "value": "3"},
                {"metric": "security_hotspots", "value": "2"},
                {"metric": "security_review_rating", "value": "5.0"},
                {"metric": "ncloc", "value": "1200"},
            ],
        ),
    ]

    extracted_metrics = GenericParser().parse(
        type_input="sonarqube", input_value=components
    )

    measures = {
        measure["metric"]: measure["value"]
        for measure in extracted_metrics["project:src/foo.py"]
    }

    assert measures == {
        "security_rating": 1.0,
        "vulnerabilities": 3.0,
        "security_hotspots": 2.0,
        "security_review_rating": 5.0,
        "ncloc": 1200.0,
    }

    for value in measures.values():
        assert isinstance(value, float)


def test_extract_keeps_security_metrics_of_fil_and_trk_components():
    """security_rating e security_review_rating vem nos dois niveis: no
    componente do projeto (TRK) e em cada arquivo (FIL). Os dois precisam
    chegar, cada um sob a sua propria chave."""
    components = [
        _component(
            "project",
            "TRK",
            [
                {"metric": "security_rating", "value": "2.0"},
                {"metric": "vulnerabilities", "value": "26"},
            ],
        ),
        _component(
            "project:src/foo.py",
            "FIL",
            [
                {"metric": "security_rating", "value": "1.0"},
                {"metric": "vulnerabilities", "value": "0"},
            ],
        ),
    ]

    extracted_metrics = GenericParser().parse(
        type_input="sonarqube", input_value=components
    )

    assert extracted_metrics["project"] == [
        {"metric": "security_rating", "value": 2.0},
        {"metric": "vulnerabilities", "value": 26.0},
    ]
    assert extracted_metrics["project:src/foo.py"] == [
        {"metric": "security_rating", "value": 1.0},
        {"metric": "vulnerabilities", "value": 0.0},
    ]


def test_extract_does_not_break_without_security_metrics():
    """Projeto sem nenhuma metrica de seguranca continua sendo extraido: so as
    medidas de seguranca deixam de ser calculadas."""
    components = [
        _component(
            "project:src/foo.py",
            "FIL",
            [
                {"metric": "coverage", "value": "82.4"},
                {"metric": "complexity", "value": "10"},
            ],
        ),
    ]

    extracted_metrics = GenericParser().parse(
        type_input="sonarqube", input_value=components
    )

    extracted = [
        measure["metric"] for measure in extracted_metrics["project:src/foo.py"]
    ]

    assert extracted == ["complexity", "coverage"]
    for metric in SECURITY_METRICS:
        assert metric not in extracted


def test_extract_drops_security_metric_without_a_numeric_value():
    """Metrica presente mas sem valor utilizavel e descartada em vez de
    derrubar a extracao das demais."""
    components = [
        _component(
            "project:src/foo.py",
            "FIL",
            [
                {"metric": "security_rating", "value": None},
                {"metric": "vulnerabilities", "value": ""},
                {"metric": "security_review_rating", "value": "nao numerico"},
                {"metric": "security_hotspots", "value": "4"},
            ],
        ),
    ]

    extracted_metrics = GenericParser().parse(
        type_input="sonarqube", input_value=components
    )

    assert extracted_metrics["project:src/foo.py"] == [
        {"metric": "security_hotspots", "value": 4.0}
    ]
