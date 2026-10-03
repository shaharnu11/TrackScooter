#!/usr/bin/env python3
"""Talk to WALL-E, English or Hebrew: mic, camera, voice. The code is walle/talker.py.

    .venv/bin/python talk.py --brain 30b-vl                     # English (the Mac)
    .venv/bin/python talk.py --lang he --brain dicta-12b         # Hebrew (the Mac)
    .venv/bin/python talk.py --brain 4b-vl                      # the XPS
    .venv/bin/python talk.py --help                             # every option
"""

from walle.talker import main

if __name__ == "__main__":
    main()
