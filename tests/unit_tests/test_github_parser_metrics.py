import os
import pytest
from genericparser.plugins.dinamic.github import ParserGithub
from tests.mockfiles.expected_return_values import (
    EXPECT_EXTRACT_METRICS,
    EXPECT_EXTRACT_METRICS_DATE_NONE,
)
import json
from unittest.mock import patch


# @pytest.mark.parametrize()
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
