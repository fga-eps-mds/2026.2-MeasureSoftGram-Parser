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


class RespostaFake:
    def __init__(self, status_code, corpo):
        self.status_code = status_code
        self._corpo = corpo

    def json(self):
        return self._corpo


def test_make_request_envia_o_token_no_cabecalho():
    with patch(
        "genericparser.plugins.dinamic.github.requests.get",
        return_value=RespostaFake(200, {"ok": True}),
    ) as get:
        assert ParserGithub()._make_request(BASE_URL, token="segredo") == {"ok": True}

    assert get.call_args.kwargs["headers"]["Authorization"] == "Bearer segredo"


def test_make_request_devolve_vazio_quando_a_api_nao_responde_200():
    with patch(
        "genericparser.plugins.dinamic.github.requests.get",
        return_value=RespostaFake(404, {"message": "Not Found"}),
    ):
        assert ParserGithub()._make_request(BASE_URL) == {}


def test_sem_filtros_toda_execucao_de_ci_entra_na_conta():
    assert ParserGithub()._should_compute_workflow_run({"name": "qualquer"}, None) is True


def test_execucao_de_workflow_fora_da_lista_fica_de_fora():
    filtros = {"workflows": ["test"], "dates": None}

    assert ParserGithub()._should_compute_workflow_run({"name": "deploy"}, filtros) is False


def test_check_requests_ignora_resposta_que_nao_e_lista_e_repetidos():
    respostas = {
        f"{BASE_URL}/issues?state=all&labels=US": [{"id": 1}, {"id": 2}],
        f"{BASE_URL}/issues?state=all&labels=Bug%20fix": [{"id": 2}, {"id": 3}],
        f"{BASE_URL}/issues?state=all&labels=vazio": {},
    }
    parser = ParserGithub()
    parser._make_request = lambda url, token=None: respostas[url]

    resultado = parser._check_requests(BASE_URL, "issues?state=all&labels=", ["US", "Bug fix", "vazio"])

    assert resultado == [{"id": 1}, {"id": 2}, {"id": 3}]


def test_extract_sem_execucoes_de_ci_traz_so_a_vazao():
    parser = ParserGithub()
    parser._get_throughput = lambda *a, **k: {"metrics": ["total_issues"], "values": [0]}
    parser._get_ci_feedback_times = lambda *a, **k: False

    resultado = parser.extract(input_file="fga-eps-mds/MeasureSoftGram-DOC", filters=None)

    assert resultado == {
        "metrics": ["total_issues"],
        "values": [0],
        "file_paths": "fga-eps-mds/MeasureSoftGram-DOC",
    }
