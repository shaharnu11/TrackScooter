#!/usr/bin/env python3
"""Load your Spotify song list into WALL-E, for playing offline.

Spotify's downloaded songs are encrypted: WALL-E cannot read them, and the
laptop cannot search them without internet. So, at home and online, this
saves the names and Spotify IDs of the songs in your playlists to
spotify/library.json. In the desert, "play Billy Joel" is looked up there
and handed to the Spotify desktop app, which plays its downloaded copy.

    python spotify_sync.py --client-id <ID>      # first time: saves the ID, opens a login
    python spotify_sync.py --list                # your playlists, numbered
    python spotify_sync.py                       # sync all playlists + Liked Songs
    python spotify_sync.py --only "Desert, Road Trip"   # just these playlists

The Spotify API cannot tell which playlists are downloaded on this laptop,
so sync the ones you switched Download on for (or everything; a song that
is not downloaded just will not play offline). Re-run after downloading
new music.

One-time setup (5 min): developer.spotify.com/dashboard -> Create app.
Any name and description. Redirect URI: http://127.0.0.1:8765/callback
(exactly). API: tick "Web API". Save, then copy the Client ID.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

SPOTIFY_DIR = Path(__file__).resolve().parent / "spotify"
CONFIG = SPOTIFY_DIR / "config.json"  # client ID + tokens: private, not in git
LIBRARY = SPOTIFY_DIR / "library.json"
PORT = 8765
# Spotify no longer accepts "localhost" redirects; the loopback IP it does.
REDIRECT = f"http://127.0.0.1:{PORT}/callback"
SCOPES = "playlist-read-private playlist-read-collaborative user-library-read"
API = "https://api.spotify.com/v1"
LIKED = "Liked Songs"


# ----- auth: authorization code with PKCE (no client secret on disk) -----
def _load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}


def _save_config(cfg: dict) -> None:
    SPOTIFY_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def _token_request(fields: dict) -> dict:
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=urllib.parse.urlencode(fields).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _login(client_id: str) -> dict:
    """Open the Spotify login in the browser; catch the answer on 127.0.0.1."""
    verifier = secrets.token_urlsafe(64)[:96]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": REDIRECT,
            "code_challenge_method": "S256",
            "code_challenge": challenge,
            "scope": SCOPES,
            "state": state,
        }
    )
    got: dict = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 — http.server's name
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            ok = "code" in got and got.get("state") == state
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "WALL-E is connected to Spotify. You can close this tab." if ok else f"Login failed: {got}"
            self.wfile.write(f"<h2>{msg}</h2>".encode())

        def log_message(self, *_args) -> None:
            pass

    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    print("Opening Spotify login in your browser…")
    print(f"(If it does not open: {url})")
    webbrowser.open(url)
    server.timeout = 300
    while "code" not in got and "error" not in got:
        server.handle_request()
    server.server_close()
    if got.get("state") != state or "code" not in got:
        sys.exit(f"Spotify login failed: {got.get('error', got)}")
    tok = _token_request(
        {
            "grant_type": "authorization_code",
            "code": got["code"],
            "redirect_uri": REDIRECT,
            "client_id": client_id,
            "code_verifier": verifier,
        }
    )
    tok["expires_at"] = time.time() + tok["expires_in"] - 60
    return tok


def _access_token(cfg: dict) -> str:
    tok = cfg.get("token")
    if tok and tok["expires_at"] > time.time():
        return tok["access_token"]
    if tok and tok.get("refresh_token"):
        try:
            new = _token_request(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": tok["refresh_token"],
                    "client_id": cfg["client_id"],
                }
            )
            new.setdefault("refresh_token", tok["refresh_token"])
            new["expires_at"] = time.time() + new["expires_in"] - 60
            cfg["token"] = new
            _save_config(cfg)
            return new["access_token"]
        except urllib.error.HTTPError:
            pass  # refresh token revoked or expired: log in again
    cfg["token"] = _login(cfg["client_id"])
    _save_config(cfg)
    return cfg["token"]["access_token"]


# ----- Web API --------------------------------------------------------------
def _get(token: str, url: str) -> dict:
    if not url.startswith("http"):
        url = API + url
    while True:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limited: wait as told
                time.sleep(int(e.headers.get("Retry-After", "2")) + 1)
                continue
            raise


def _pages(token: str, url: str):
    while url:
        page = _get(token, url)
        yield from page.get("items", [])
        url = page.get("next")


def _track(item: dict) -> dict | None:
    t = item.get("track") or item.get("item")
    if not t or t.get("type") != "track" or not t.get("uri") or t.get("is_local"):
        return None  # podcasts, removed songs, local files
    return {
        "name": t["name"],
        "artists": [a["name"] for a in t.get("artists", [])],
        "album": (t.get("album") or {}).get("name", ""),
        "uri": t["uri"],
    }


def playlists(token: str) -> list[dict]:
    return [p for p in _pages(token, "/me/playlists?limit=50") if p]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client-id", help="Your Spotify app's Client ID (saved after the first time)")
    parser.add_argument("--list", action="store_true", help="Show your playlists and stop")
    parser.add_argument("--only", help='Comma-separated playlist names or numbers from --list, e.g. "Desert, 3"')
    parser.add_argument("--no-liked", action="store_true", help="Skip Liked Songs")
    parser.add_argument("--no-albums", action="store_true", help="Skip saved albums")
    args = parser.parse_args()

    cfg = _load_config()
    if args.client_id:
        cfg["client_id"] = args.client_id.strip()
        cfg.pop("token", None)
        _save_config(cfg)
    if not cfg.get("client_id"):
        sys.exit("First time: python spotify_sync.py --client-id <ID>   (see the setup notes: --help)")
    token = _access_token(cfg)
    me = _get(token, "/me")
    print(f"Spotify: {me.get('display_name') or me.get('id')}")

    lists = playlists(token)
    if args.list:
        for i, p in enumerate(lists, 1):
            print(f"{i:3}. {p['name']}  ({(p.get('tracks') or p.get('items') or {}).get('total', '?')} songs)")
        return

    wanted = None
    if args.only:
        wanted = set()
        for part in (s.strip() for s in args.only.split(",")):
            if part.isdigit() and 1 <= int(part) <= len(lists):
                wanted.add(lists[int(part) - 1]["id"])
            else:
                hit = [p["id"] for p in lists if p["name"].lower() == part.lower()]
                if not hit:
                    sys.exit(f'No playlist named "{part}". See: python spotify_sync.py --list')
                wanted |= set(hit)

    tracks: dict[str, dict] = {}
    out_lists = []

    def add(t: dict | None, list_name: str) -> None:
        if t is None:
            return
        t = tracks.setdefault(t["uri"], {**t, "playlists": []})
        if list_name not in t["playlists"]:
            t["playlists"].append(list_name)

    for p in lists:
        if wanted is not None and p["id"] not in wanted:
            continue
        n = 0
        try:
            # /playlists/{id}/tracks answers 403 now, even for your own
            # playlists; Spotify moved it to /items. Use the link it gives.
            href = (p.get("items") or p.get("tracks") or {}).get("href") or f"/playlists/{p['id']}/items"
            for item in _pages(token, f"{href}?limit=100"):
                add(_track(item), p["name"])
                n += 1
        except urllib.error.HTTPError as e:
            # Playlists made by someone else ("Metallica Greatest Hits" by
            # Pettson_jr) and Spotify's own mixes answer 403 to apps. Copy
            # them in the app: ⋯ -> Add to other playlist -> New playlist.
            owner = (p.get("owner") or {}).get("display_name") or "someone else"
            print(f"  skipped {p['name']} (by {owner}): Spotify says {e.code}")
            continue
        out_lists.append({"name": p["name"], "uri": p["uri"], "count": n})
        print(f"  {p['name']}: {n} songs")

    if not args.no_liked and not args.only:
        n = 0
        for item in _pages(token, "/me/tracks?limit=50"):
            add(_track(item), LIKED)
            n += 1
        out_lists.append({"name": LIKED, "uri": f"{me['uri']}:collection", "count": n})
        print(f"  {LIKED}: {n} songs")

    # Saved albums ("Discovery", "Trilogy"…) are their own list in Spotify,
    # apart from Liked Songs. Each becomes a list WALL-E can play by name.
    if not args.no_albums and not args.only:
        albums = 0
        for saved in _pages(token, "/me/albums?limit=50"):
            al = saved.get("album") or saved.get("item") or {}
            if not al.get("uri"):
                continue
            n = 0
            page = al.get("tracks") or al.get("items") or {}
            while page:
                for t in page.get("items", []):
                    if t.get("uri") and t.get("type") == "track":
                        add(
                            {
                                "name": t["name"],
                                "artists": [a["name"] for a in t.get("artists", [])],
                                "album": al["name"],
                                "uri": t["uri"],
                            },
                            al["name"],
                        )
                        n += 1
                page = _get(token, page["next"]) if page.get("next") else None
            out_lists.append({"name": al["name"], "uri": al["uri"], "count": n, "album": True})
            albums += 1
        print(f"  Saved albums: {albums}")

    SPOTIFY_DIR.mkdir(parents=True, exist_ok=True)
    LIBRARY.write_text(
        json.dumps(
            {
                "synced": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "user": me.get("display_name") or me.get("id"),
                "playlists": out_lists,
                "tracks": list(tracks.values()),
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"\nSaved {len(tracks)} songs from {len(out_lists)} lists to {LIBRARY}")
    print("WALL-E reads it at start. Keep those playlists downloaded in the Spotify app.")


if __name__ == "__main__":
    main()
