# Copyright (c) 2016, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of ytranslate nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""This file contains the GameEngine class."""

from datetime import datetime
import logging
import os

from enum import Enum

from client import GUIClient
from config import Settings
from sharp.engine import SharpScript

class Level(Enum):

    """Enumeration for a feature level.

    Features at the top level have the value "engine". They will be
    common across all worlds and characters. Features are often defined
    at the world level (common across characters) or at the character
    level (specific to this character).

    For instance, look at the macros, triggers and aliases.

    """

    engine = 1
    world = 2
    character = 3
    category = 4


class CustomFormatter(logging.Formatter):

    """Special formatter to add hour and minute."""

    def format(self, record):
        """Add special placeholders for shorter messages."""
        now = datetime.now()
        record.hour = now.hour
        record.minute = now.minute
        return logging.Formatter.format(self, record)


class GameEngine:

    """A class representing the game engine.

    An instance of this class is to be created each time the program
    runs.  It doesn't handle thegraphical user interface, but centralizes
    about anything else:  the main configuration, world configuration
    of different games, aliases, macros, triggers and so on.  The
    GUI has a direct access to the engine and can therefore access it.

    """

    def __init__(self):
        if not os.path.exists("logs"):
            os.mkdir("logs")

        self.loggers = {}
        self.logger = self.create_logger("")
        self.settings = Settings(self)
        self.worlds = {}
        self.default_world = None
        self.level = Level.engine
        self.logger.info("CocoMUD engine started")

    def create_logger(self, name, filename=None):
        """Create and return a new logger.

        The name should be a string like 'sharp' to create the child
        logger 'cocomud.sharp'.  If no filename is specified, the
        handler for the file 'logs/{name}.log" will be created.

        """
        if not name:
            filename = os.path.join("logs", "main.log")
            name = "cocomud"
        else:
            filename = filename or os.path.join("logs", name + ".log")
            name = "cocomud." + name

        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        formatter = CustomFormatter(
                "%(hour)02d:%(minute)02d [%(levelname)s] %(message)s")

        # If it's the main logger, create a stream handler
        if name == "cocomud":
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)

        # Create the file handler
        handler = logging.FileHandler(filename, encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.loggers[name] = logger
        return logger

    def load(self):
        """Load the configuration."""
        self.logger.info("Loading the user's configuration...")
        self.settings.load()
        self.TTS_on = self.settings["options.TTS.on"]
        self.TTS_outside = self.settings["options.TTS.outside"]

        # For each world, set the game engine
        for world in self.worlds.values():
            world.engine = self

    def open(self, host, port, world):
        """Connect to the specified host and port.

        This method creates and returns a 'GUIClient' class initialized
        with the specified information.

        """
        self.logger.info("Creating a client for {host}:{port}".format(
                host=host, port=port))

        client = GUIClient(host, port, engine=self, world=world)
        sharp_engine = SharpScript(self, client, world)
        world.client = client
        client.sharp_engine = sharp_engine
        world.sharp_engine = sharp_engine
        return client

    def open_help(self, name):
        """Open the selected help file in HTML format.

        This method open the browser with the appropriate file.
        The file is the one in the user's language, unless it cannot
        be found.

        """
        lang = self.settings.get_language()
        filename = name + ".html"
        path = os.path.join("doc", lang, filename)
        if os.path.exists(path):
            self.logger.debug("Open the help file for {} (lang={})".format(
                    name, lang))
            os.startfile(path)
            return

        # Try English
        path = os.path.join("doc", "en", filename)
        if os.path.exists(path):
            self.logger.debug("Open the help file for {} (lang=en)".format(
                    name))
            os.startfile(path)
            return

        # Neither worked
        self.logger.debug("The documentation for the {} help file " \
                "cannot be found, either using lang={} or lang=en".format(
                name, lang))
