# constants.py

import os

IN_FLATPAK = bool(os.getenv("FLATPAK_ID"))
IN_SNAP = bool(os.getenv("FLATPAK_ID"))

def get_xdg_home(env, default):
    if IN_FLATPAK:
        return os.getenv(env)
    base = os.getenv(env) or os.path.expanduser(default)
    path = os.path.join(base, "com.jeffser.Alpaca")
    if not os.path.exists(path):
        os.makedirs(path)
    return path

DATA_DIR = get_xdg_home("XDG_DATA_HOME", "~/.local/share")
CONFIG_DIR = get_xdg_home("XDG_CONFIG_HOME", "~/.config")
CACHE_DIR = get_xdg_home("XDG_CACHE_HOME", "~/.cache")

SIDEBAR_MENU = [
    { # Section
        'items': [
            { # Item
                'title': _("Home"),
                'icon-name': "user-home-symbolic",
                'page-name': 'home'
            }
        ]
    },
    { # Section
        'title': _("Albums"),
        'items': [
            { # Item
                'title': _("All"),
                'icon-name': "music-queue-symbolic",
                'page-name': 'albums'
            },
            { # Item
                'title': _("Random"),
                'icon-name': "playlist-shuffle-symbolic",
                'page-name': 'albums-random'
            },
            { # Item
                'title': _("Favorites"),
                'icon-name': "starred-symbolic",
                'page-name': 'albums-favorites'
            },
            { # Item
                'title': _("Recently Added"),
                'icon-name': "list-add-symbolic",
                'page-name': 'albums-recently-added'
            },
            { # Item
                'title': _("Recently Played"),
                'icon-name': "media-playback-start-symbolic",
                'page-name': 'albums-recently-played'
            },
            { # Item
                'title': _("Most Played"),
                'icon-name': "media-playlist-repeat-symbolic",
                'page-name': 'albums-most-played'
            }
        ]
    },
    {
        'items': [
            { # Item
                'title': _("Artists"),
                'icon-name': "music-artist-symbolic",
                'page-name': 'artists'
            },
            { # Item
                'title': _("Songs"),
                'icon-name': "music-note-symbolic",
                'page-name': 'songs'
            },
            { # Item
                'title': _("Radios"),
                'icon-name': "sound-wave-symbolic",
                'page-name': 'radios'
            },
            { # Item
                'title': _("Playlists"),
                'icon-name': "playlist-symbolic",
                'page-name': 'playlists'
            }
        ]
    }
]
