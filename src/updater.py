﻿# Copyright (c) 2016, LE GOFF Vincent
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


"""Auto-updater of the CocoMUD client."""

import wx

from autoupdate import AutoUpdate
from version import BUILD

class DummyUpdater(wx.Frame):

    """Dummy updater, to which updaters should inherit."""

    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        self.autoupdater = None
        self.default_text = "Loading..."
        self.progress = 0

        # Event binding
        self.Bind(EVT_GAUGE, self.OnGauge)
        self.Bind(EVT_TEXT, self.OnText)
        self.Bind(EVT_FORCE_DESTROY, self.OnForceDestroy)
        self.Bind(EVT_AVAILABLE_UPDATE, self.OnAvailableUpdate)

    def create_updater(self, just_checking=False):
        """Create a new autoupdater instance."""
        self.autoupdate = AutoUpdate(BUILD, self, just_checking=just_checking)
        self.autoupdate.start()

    def OnGauge(self, e):
        """The progress indicator changes."""
        pass

    def OnText(self, e):
        """The text of the indicator changes."""
        pass

    def OnForceDestroy(self, e):
        """Ask for the window's destruction."""
        pass

    def OnAvailableUpdate(self, e):
        """An update is available."""
        pass

    def UpdateGauge(self, value):
        """Change the level indicator."""
        evt = GaugeEvent(myEVT_GAUGE, -1, value)
        wx.PostEvent(self, evt)

    def UpdateText(self, text):
        """Change the text."""
        evt = TextEvent(myEVT_TEXT, -1, text)
        wx.PostEvent(self, evt)

    def AskDestroy(self):
        evt = ForceDestroyEvent(myEVT_FORCE_DESTROY, -1, None)
        wx.PostEvent(self, evt)

    def AvailableUpdate(self, build):
        """Updates are available."""
        evt = AvailableUpdateEvent(myEVT_AVAILABLE_UPDATE, -1, build)
        wx.PostEvent(self, evt)


class Updater(DummyUpdater):

    """Graphical updater with a gauge."""

    def __init__(self, parent, just_checking=False):
        DummyUpdater.__init__(self, parent)
        self.create_updater(just_checking)
        self.InitUI()
        self.Show()
        self.Center()

    def InitUI(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        self.text = wx.TextCtrl(panel, value="Loading...", size=(200, 400),
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.gauge = wx.Gauge(panel, range=100, size=(250, 25))
        self.cancel = wx.Button(panel, wx.ID_CANCEL)

        # Window design
        sizer.Add(self.text)
        sizer.Add(self.gauge)
        sizer.Add(self.cancel)

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)

    def OnGauge(self, e):
        self.gauge.SetValue(e.GetValue())
        text = self.default_text
        text += " ({}%)".format(e.GetValue())
        self.text.SetValue(text)

    def OnText(self, e):
        self.default_text = e.GetValue()
        self.text.SetValue(e.GetValue())

    def OnForceDestroy(self, e):
        self.Destroy()

    def OnCancel(self, e):
        """The user clicks on 'cancel'."""
        value = wx.MessageBox("Do you really want to cancel this update?",
                "Confirm", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        if value == wx.YES:
            self.Destroy()


# Events
myEVT_GAUGE = wx.NewEventType()
EVT_GAUGE = wx.PyEventBinder(myEVT_GAUGE, 1)

class GaugeEvent(wx.PyCommandEvent):

    """Change the value of the gaughe."""

    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Return the event's value."""
        return self._value

myEVT_TEXT = wx.NewEventType()
EVT_TEXT = wx.PyEventBinder(myEVT_TEXT, 1)

class TextEvent(wx.PyCommandEvent):

    """Change the value of the text field."""

    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Return the event's value."""
        return self._value


myEVT_FORCE_DESTROY = wx.NewEventType()
EVT_FORCE_DESTROY = wx.PyEventBinder(myEVT_FORCE_DESTROY, 1)

class ForceDestroyEvent(wx.PyCommandEvent):

    """Force the application to terminate."""

    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Return the event's value."""
        return self._value


myEVT_AVAILABLE_UPDATE = wx.NewEventType()
EVT_AVAILABLE_UPDATE = wx.PyEventBinder(myEVT_AVAILABLE_UPDATE, 1)

class AvailableUpdateEvent(wx.PyCommandEvent):

    """Signal that an update is available."""

    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Return the event's value."""
        return self._value


# AppMainLoop
if __name__ == "__main__":
    app = wx.App()
    frame = Updater(None)
    app.MainLoop()