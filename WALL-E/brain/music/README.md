# WALL-E's music

Drop songs here: mp3, m4a, wav, flac, ogg. Sub-folders are fine. Not in git.

Name files `Artist - Title.mp3` and WALL-E says "Piano Man by Billy Joel"
and finds it when you ask for "Billy Joel" or "Piano Man".

Say to him (`talk_english.py`):

| You say | He does |
|---|---|
| "play some music" / "play something" | a random song, then keeps going like a radio |
| "play Billy Joel" | the best file-name match, or a random song if none |
| "next song" / "skip" | another song |
| "what's playing?" | says the song name |
| "stop the music" | stops |

The music drops to 20% while you talk to him and while he answers.

## Spotify (offline)

He also plays your Spotify songs, through the Spotify **desktop** app (the
web player cannot play offline). Asked for something, he looks in this
folder first, then in your Spotify list.

1. In the desktop app, switch on Download (↓) for the playlists you want.
2. Online, once: `python spotify_sync.py` (first time `--client-id <ID>`,
   see `--help`). It saves your playlists + Liked Songs to
   `spotify/library.json`. Re-run after downloading new music.
3. Before a trip: open Spotify once online (it needs that every 30 days),
   and try Settings → Offline mode at home.

"play my Chill playlist", "play Omer Adam", "next song", "what's playing",
"stop the music".

Spotify cannot tell a program which songs are downloaded. So WALL-E starts
the song first, watches that it really plays, and only then names it. A
song that will not start (offline and not downloaded) is written to
`spotify/not_downloaded.json` and never picked again; he tries up to 3
songs, then says it may not be downloaded. Delete that file after
downloading more, to give those songs another chance. Playlists made by other people cannot be read by the
Spotify API (403), so they cannot be asked for by name.
