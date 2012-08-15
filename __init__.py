#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# python 2.5.4
#
# __init__ r88_structurama
#
# run this file to start r88_structurama
#
# (C) Timotheus Andreas Klein 2012 - Tim.Klein@gmx.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import wx
import mvc

if __name__ == '__main__':
    app = wx.App(False)
    controller = mvc.Controller(app)
    app.MainLoop()

else:
    print 'r88_Structurama was imported. r88_Structurama is free software.'
    
