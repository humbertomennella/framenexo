"""Commit only the non-publishing output produced by the frequent scout."""
import base64
import os
import subprocess


def git(*args, **kwargs):
    return subprocess.run(["git", *args], check=True, text=True, **kwargs)


git(
    "add",
    "data/candidates.json",
    "data/editorial-log.json",
    "data/publishing-state.json",
    "data/scout-state.json",
)
changed = subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 1
if changed:
    git("config", "user.name", "github-actions[bot]")
    git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    git("commit", "-m", "chore: atualiza escuta editorial")
    env = os.environ.copy()
    token = env.pop("GITHUB_TOKEN")
    auth = base64.b64encode(("x-access-token:" + token).encode()).decode()
    env.update(
        GIT_CONFIG_COUNT="1",
        GIT_CONFIG_KEY_0="http.extraHeader",
        GIT_CONFIG_VALUE_0="Authorization: Basic " + auth,
    )
    git("push", "origin", "HEAD:main", env=env)
print("Scout data committed." if changed else "No scout changes to commit.")
