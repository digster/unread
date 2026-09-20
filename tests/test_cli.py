"""Exercise CLI filtering through HTTP requests and temporary URL files."""

from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from unread_articles import cli

runner = CliRunner()


@pytest.fixture
def cli_context(monkeypatch, tmp_path):
    """Isolate output and git effects while exercising the real fetch/save path."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RAINDROP_API_TOKEN", "test-token")
    # Mark the temporary directory as the root so tests never target this repo.
    (tmp_path / ".git").mkdir()
    commit = Mock(return_value=True)
    monkeypatch.setattr(cli, "commit_and_push", commit)
    return tmp_path / "urls.txt", commit


@pytest.mark.parametrize("command", ["fetch", "sync"])
@pytest.mark.parametrize("match_any", [False, True])
@pytest.mark.parametrize("custom_options", [False, True])
def test_tag_matching(command, match_any, custom_options, cli_context, httpx_mock):
    """Both commands preserve existing options while selecting AND or OR."""
    urls_path, commit = cli_context
    httpx_mock.add_response(json={"items": [{"link": "https://example.com/article"}]})
    args = [command, "python", "machine learning"]
    if match_any:
        args.append("--or")
    if custom_options:
        args.extend(["-c", "42"])
        if command == "sync":
            args.extend(["-m", "update selected articles"])

    result = runner.invoke(cli.app, args)

    assert result.exit_code == 0, result.output
    expected_search = '#"python" #"machine learning"'
    if match_any:
        expected_search += " match:OR"
    request = httpx_mock.get_request()
    assert request.url.params["search"] == expected_search
    assert request.url.path == f"/rest/v1/raindrops/{42 if custom_options else 0}"
    assert urls_path.read_text() == "https://example.com/article\n"
    assert f"({'OR' if match_any else 'AND'})" in result.output
    if command == "sync":
        commit.assert_called_once_with(
            files=[str(urls_path)],
            message="update selected articles" if custom_options else None,
        )
    else:
        commit.assert_not_called()


@pytest.mark.parametrize("command", ["fetch", "sync"])
@pytest.mark.parametrize("options", [[], ["--or"]])
def test_missing_tags(command, options, cli_context, httpx_mock):
    urls_path, commit = cli_context

    result = runner.invoke(cli.app, [command, *options])

    assert result.exit_code == 2
    assert "Missing argument" in result.output
    assert not urls_path.exists()
    assert httpx_mock.get_requests() == []
    commit.assert_not_called()


def test_or_sync_without_changes(cli_context, httpx_mock):
    urls_path, commit = cli_context
    urls_path.write_text("")
    commit.return_value = False
    httpx_mock.add_response(json={"items": []})

    result = runner.invoke(cli.app, ["sync", "python", "ai", "--or"])

    assert result.exit_code == 0, result.output
    assert urls_path.read_text() == ""
    assert "No changes to commit" in result.output
    commit.assert_called_once_with(files=[str(urls_path)], message=None)
