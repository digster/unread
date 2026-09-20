# Unread Articles

Fetch bookmarked URLs from [Raindrop.io](https://raindrop.io) by tag and serve a random redirect via GitHub Pages.

## How it works

1. **CLI** fetches bookmarks matching your tags from Raindrop.io's API
2. URLs are saved to `urls.txt` (one per line)
3. **GitHub Pages** serves `index.html`, which picks a random URL and redirects

## Setup

```bash
# Install dependencies
uv sync

# Configure your Raindrop.io API token
cp .env.example .env
# Edit .env and add your token (get one at https://app.raindrop.io/settings/integrations)
```

## Usage

```bash
# Fetch bookmarks by tag → saves to urls.txt
uv run unread-articles fetch python

# Multiple tags (AND logic — bookmarks must match all)
uv run unread-articles fetch python ai

# Match any supplied tag (OR logic)
uv run unread-articles fetch python ai --or

# Quote tags that contain spaces
uv run unread-articles fetch "machine learning" ai --or

# Fetch from a specific collection (default: 0 = all)
uv run unread-articles fetch python -c 12345678

# Fetch + commit + push in one step
uv run unread-articles sync python

# Fetch bookmarks matching either tag, then commit and push
uv run unread-articles sync python ai --or

# With a custom commit message
uv run unread-articles sync python -m "add python articles"
```

Both commands require at least one tag and use AND matching by default. Add
`--or` to match any supplied tag; it also works with `--collection` / `-c` and
the sync command's `--message` / `-m` option. The progress output shows the
selected matching mode. A single tag matches the same bookmarks in either mode.

## GitHub Pages Setup

1. Push this repo to GitHub
2. Go to **Settings → Pages**
3. Set source to **Deploy from a branch** → `main` / `/ (root)`
4. Visit `https://<username>.github.io/unread-articles/` — you'll be redirected to a random saved article

## Development

```bash
# Run tests
uv run pytest -v

# Run with verbose output
uv run unread-articles --help
```

## Getting a Raindrop.io API Token

1. Go to [Raindrop.io Integrations](https://app.raindrop.io/settings/integrations)
2. Click **Create new app**
3. Under the app, click **Create test token**
4. Copy the token into your `.env` file
