# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
from blinker import signal

conversion_started = signal('conversion_started')
conversion_error = signal('conversion_error')
conversion_complete = signal('conversion_complete')
