import os
import pytest
from genericparser.plugins.dinamic.github import ParserGithub
from tests.mockfiles.expected_return_values import (
    EXPECT_EXTRACT_METRICS,
    EXPECT_EXTRACT_METRICS_DATE_NONE,
)
import json
import requests
from unittest.mock import patch


BASE_URL = "https://api.github.com/repos/fga-eps-mds/MeasureSoftGram-DOC"


def mock_requests(url, token=None):
    if url == BASE_URL:
        return_file = open("tests/mockfiles/response_api_github_general.json")
        return json.loads(return_file.read())
    if url == f"{BASE_URL}/actions/runs":
        return_file = open("tests/mockfiles/response_api_github_ci_feedback_times.json")
        return json.loads(return_file.read())
    if url == f"{BASE_URL}/issues?state=all&labels=US":
        return_file = open("tests/mockfiles/response_api_github_throughput.json")
        return json.loads(return_file.read())


def get_object():
    parser = ParserGithub()
    parser._make_request = mock_requests
    return parser


def test_extract_method_all_filters():
    parserObject = get_object()
    assert (
        parserObject.extract(**{
            "input_file": "fga-eps-mds/MeasureSoftGram-DOC",
            "filters": {"labels": "US",
                        "workflows": ["pages build and deployment"],
                        "dates": "20/06/2023-15/07/2023"}
        })
        == EXPECT_EXTRACT_METRICS
    )


def test_extract_method_date_none():
    parserObject = get_object()
    assert (
        parserObject.extract(**{
            "input_file": "fga-eps-mds/MeasureSoftGram-DOC",
            "filters": {"labels": "US",
                        "workflows": ["pages build and deployment"],
                        "dates": None}
        })
        == EXPECT_EXTRACT_METRICS_DATE_NONE
    )


# Token precedence tests

def test_token_from_input_file_dict():
    """Token from input_file dict takes highest precedence."""
    captured = {}

    def capturing_request(url, token=None):
        captured["token"] = token
        return mock_requests(url, token)

    parser = ParserGithub(token="instance-token")
    parser._make_request = capturing_request

    with patch.dict(os.environ, {"GITHUB_TOKEN": "env-token"}):
        parser.extract(**{
            "input_file": {
                "repository": "fga-eps-mds/MeasureSoftGram-DOC",
                "token": "dict-token",
            },
            "filters": {"labels": "US", "workflows": ["pages build and deployment"], "dates": None},
        })

    assert captured["token"] == "dict-token"


def test_token_falls_back_to_env_when_dict_has_no_token():
    """When input_file dict has no 'token', GITHUB_TOKEN env var is used."""
    captured = {}

    def capturing_request(url, token=None):
        captured["token"] = token
        return mock_requests(url, token)

    parser = ParserGithub(token="instance-token")
    parser._make_request = capturing_request

    with patch.dict(os.environ, {"GITHUB_TOKEN": "env-token"}, clear=False):
        parser.extract(**{
            "input_file": {"repository": "fga-eps-mds/MeasureSoftGram-DOC"},
            "filters": {"labels": "US", "workflows": ["pages build and deployment"], "dates": None},
        })

    assert captured["token"] == "env-token"


def test_token_falls_back_to_instance_when_no_dict_token_and_no_env():
    """When input_file dict has no 'token' and GITHUB_TOKEN is unset, self.token is used."""
    captured = {}

    def capturing_request(url, token=None):
        captured["token"] = token
        return mock_requests(url, token)

    parser = ParserGithub(token="instance-token")
    parser._make_request = capturing_request

    env_without_github = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
    with patch.dict(os.environ, env_without_github, clear=True):
        parser.extract(**{
            "input_file": {"repository": "fga-eps-mds/MeasureSoftGram-DOC"},
            "filters": {"labels": "US", "workflows": ["pages build and deployment"], "dates": None},
        })

    assert captured["token"] == "instance-token"


def test_make_request_returns_empty_dict_on_request_exception():
    parser = ParserGithub()

    with patch(
        "genericparser.plugins.dinamic.github.requests.get",
        side_effect=requests.exceptions.ConnectionError,
    ):
        assert parser._make_request(BASE_URL) == {}


# Security alerts (SCM)

def _parser_with_alerts(alert_pages):
    """Parser cujo _make_request responde as paginas de alertas informadas e
    delega o resto para o mock geral."""
    parser = ParserGithub()

    def request(url, token=None):
        if "/dependabot/alerts" in url:
            page = int(url.split("&page=")[1])
            return alert_pages[page - 1]
        return mock_requests(url, token)

    parser._make_request = request
    return parser


def test_get_security_alerts_counts_open_and_closed():
    parser = _parser_with_alerts([
        [
            {"number": 1, "state": "open"},
            {"number": 2, "state": "fixed"},
            {"number": 3, "state": "dismissed"},
            {"number": 4, "state": "open"},
        ]
    ])

    assert parser._get_security_alerts(BASE_URL) == {
        "metrics": ["security_alerts_open", "security_alerts_closed"],
        "values": [2, 2],
    }


def test_get_security_alerts_without_alerts_returns_zeros():
    """Repositorio sem alerta algum e resposta valida, diferente de alerta
    indisponivel."""
    parser = _parser_with_alerts([[]])

    assert parser._get_security_alerts(BASE_URL)["values"] == [0, 0]


def test_get_security_alerts_paginates():
    parser = _parser_with_alerts([
        [{"number": index, "state": "open"} for index in range(100)],
        [{"number": 100, "state": "fixed"}],
    ])

    assert parser._get_security_alerts(BASE_URL)["values"] == [100, 1]


@pytest.mark.parametrize("unavailable_response", [{}, None, {"message": "Forbidden"}])
def test_get_security_alerts_returns_false_when_unavailable(unavailable_response):
    """Sem Dependabot habilitado ou sem permissao de security_events a API
    responde 403/404 e _make_request devolve {}; a extracao segue sem as
    metricas."""
    parser = _parser_with_alerts([unavailable_response])

    assert parser._get_security_alerts(BASE_URL) is False


def test_extract_includes_security_alert_metrics():
    parser = _parser_with_alerts([
        [{"number": 1, "state": "open"}, {"number": 2, "state": "fixed"}]
    ])

    extracted = parser.extract(**{
        "input_file": "fga-eps-mds/MeasureSoftGram-DOC",
        "filters": {"labels": "US",
                    "workflows": ["pages build and deployment"],
                    "dates": None}
    })

    metrics = dict(zip(extracted["metrics"], extracted["values"]))

    assert metrics["security_alerts_open"] == 1
    assert metrics["security_alerts_closed"] == 1


def test_extract_without_security_alerts_keeps_the_other_metrics():
    parserObject = get_object()

    extracted = parserObject.extract(**{
        "input_file": "fga-eps-mds/MeasureSoftGram-DOC",
        "filters": {"labels": "US",
                    "workflows": ["pages build and deployment"],
                    "dates": None}
    })

    assert "security_alerts_open" not in extracted["metrics"]
    assert "total_issues" in extracted["metrics"]
    assert "sum_ci_feedback_times" in extracted["metrics"]
