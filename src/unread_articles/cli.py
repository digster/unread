"""CLI interface for unread-articles: fetch and sync Raindrop.io bookmarks."""

import os
from pathlib import Path
from typing import Annotated, Optional

import typer
from dotenv import load_dotenv

from unread_articles.git_ops import commit_and_push
from unread_articles.raindrop import fetch_all_urls, save_urls

# Load .env from the project root (where the CLI is invoked)
load_dotenv()

app = typer.Typer(
    name="unread-articles",
    help="Fetch bookmarked URLs from Raindrop.io by tag.",
    no_args_is_help=True,
)

# Shared type aliases for CLI parameters
Tags = Annotated[
    list[str],
    typer.Argument(help="Tags to filter by (AND by default; --or matches any tag)."),
]
MatchAnyOpt = Annotated[
    bool,
    typer.Option("--or", help="Match any supplied tag instead of all tags (OR logic)."),
]
CollectionOpt = Annotated[
    int,
    typer.Option("--collection", "-c", help="Raindrop collection ID (0 = all)."),
]


def _get_token() -> str:
    """Retrieve the Raindrop API token from environment, or exit with an error."""
    token = os.environ.get("RAINDROP_API_TOKEN")
    if not token:
        typer.echo("Error: RAINDROP_API_TOKEN not set. Add it to .env or export it.", err=True)
        raise typer.Exit(code=1)
    return token


def _resolve_urls_path() -> str:
    """Resolve the path to urls.txt relative to the git repo root."""
    # Walk up from cwd to find the git root, fallback to cwd
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").exists():
            return str(parent / "urls.txt")
    return str(cwd / "urls.txt")


@app.command()
def fetch(
    tags: Tags,
    collection: CollectionOpt = 0,
    match_any: MatchAnyOpt = False,
) -> None:
    """Fetch URLs from Raindrop.io by tag and save to urls.txt."""
    token = _get_token()
    urls_path = _resolve_urls_path()

    match_mode = "OR" if match_any else "AND"
    typer.echo(f"Fetching bookmarks tagged ({match_mode}): {', '.join(tags)}")
    urls = fetch_all_urls(token, tags, collection_id=collection, match_any=match_any)

    save_urls(urls, path=urls_path)
    typer.echo(f"Saved {len(urls)} URLs to {urls_path}")


@app.command()
def sync(
    tags: Tags,
    collection: CollectionOpt = 0,
    message: Annotated[
        Optional[str],
        typer.Option("--message", "-m", help="Custom git commit message."),
    ] = None,
    match_any: MatchAnyOpt = False,
) -> None:
    """Fetch URLs from Raindrop.io, save to urls.txt, then commit and push."""
    token = _get_token()
    urls_path = _resolve_urls_path()

    match_mode = "OR" if match_any else "AND"
    typer.echo(f"Fetching bookmarks tagged ({match_mode}): {', '.join(tags)}")
    urls = fetch_all_urls(token, tags, collection_id=collection, match_any=match_any)

    save_urls(urls, path=urls_path)
    typer.echo(f"Saved {len(urls)} URLs to {urls_path}")

    typer.echo("Committing and pushing...")
    committed = commit_and_push(files=[urls_path], message=message)
    if committed:
        typer.echo("Done!")
    else:
        typer.echo("No changes to commit — URLs are already up to date.")
