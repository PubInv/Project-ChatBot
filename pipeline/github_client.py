"""Small GitHub API client used by the workbook refresh."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class GitHubClient:
    def __init__(self) -> None:
        # This pipeline is intended to run in GitHub Actions, where GITHUB_TOKEN
        # is provided to the job.
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("ERROR: GITHUB_TOKEN is required. Run this workflow in GitHub Actions.")

        # The User-Agent is required by GitHub API etiquette.
        self.headers = {"User-Agent": "project-chatbot-workbook-refresh/1.0"}

        # API requests ask for GitHub's JSON response format.
        self.api_headers = {**self.headers, "Accept": "application/vnd.github+json"}

        # Authenticate API requests made by the workflow.
        self.api_headers["Authorization"] = f"Bearer {token}"

    def latest_commit(self, owner: str, repo: str, path: str = "", ref: str = "") -> str:
        """Return the latest commit timestamp for a repo or one file path."""
        # The commits endpoint returns newest commits first when per_page=1.
        params = ["per_page=1"]

        # Blob links include a branch/ref and a file path. Both matter for
        # repositories whose default branch differs from the blob link branch.
        if ref:
            params.append(f"sha={quote(ref)}")
        if path:
            params.append(f"path={quote(path)}")

        url = f"https://api.github.com/repos/{owner}/{repo}/commits?{'&'.join(params)}"

        try:
            # commits is a list; the first item is the newest matching commit.
            commits = self.get_json(url)
            if commits:
                commit = commits[0].get("commit", {})
                return (commit.get("committer") or commit.get("author") or {}).get("date", "")
        except (HTTPError, URLError, OSError, KeyError, TypeError):
            # If a file-specific lookup fails, do not substitute repo activity.
            # That would make old project idea files look fresh.
            pass
        if path:
            return ""
        return self.repo_pushed_at(owner, repo)

    def repo_pushed_at(self, owner: str, repo: str) -> str:
        """Return repository pushed_at as a fallback activity timestamp."""
        try:
            return self.get_json(f"https://api.github.com/repos/{owner}/{repo}").get("pushed_at", "")
        except (HTTPError, URLError, OSError):
            return ""

    def get_json(self, url: str):
        """GET a GitHub API URL and decode the JSON body."""
        with urlopen(Request(url, headers=self.api_headers), timeout=12) as response:
            return json.loads(response.read().decode("utf-8", errors="ignore"))
