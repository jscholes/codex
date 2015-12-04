# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import accessible_output2 as ao
from accessible_output2 import outputs

import application

def get_screen_reader_outputs():
    available_outputs = ao.get_output_classes()
    sr_outputs = []
    system_outputs = ['PCTalker', 'SAPI4', 'SAPI5']
    for output in available_outputs:
        try:
            # output.name doesn't seem to be defined for all output classes
            if output.__name__ not in system_outputs:
                sr_outputs.append(output())
        except outputs.base.OutputError:
            pass

    return sr_outputs

def setup():
    # We don't want SAPI5 or PC Talker output, only screen reader
    sr_outputs = get_screen_reader_outputs()
    speaker = outputs.auto.Auto()
    speaker.outputs = sr_outputs
    application.speaker = speaker
