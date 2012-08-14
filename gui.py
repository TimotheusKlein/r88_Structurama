#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# GUI Part r88_structurama
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
 
import sys
import wx
import wx.grid as grd
import wx.lib.scrolledpanel as scrolled

class AttDefFrame(wx.Frame):
    def __init__(self, menudata, tabsdata):
        wx.Frame.__init__(self, None, -1, title='r88_Structurama',
                pos=wx.DefaultPosition, size=(955,400),
                style=wx.DEFAULT_FRAME_STYLE)
        self.createMenuBar(menudata)
        self.attdeftabs = AttDefTabs(self, -1, tabsdata)
        self.oldconditions = {}

    def createMenuBar(self, menuData):
        menuBar = wx.MenuBar()
        for eachMenuData in menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1:]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)

    def createMenu(self, menuItems):
        menu = wx.Menu()
        for eachType, eachLabel, eachStatus, eachHandler in menuItems:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            if eachType == 'c':
                menuItem = menu.AppendCheckItem(-1, eachLabel, eachStatus)
                self.Bind(wx.EVT_MENU, eachHandler, menuItem)   
            else:
                menuItem = menu.Append(-1, eachLabel, eachStatus)
                self.Bind(wx.EVT_MENU, eachHandler, menuItem)
        return menu

    def updatecontrols(self, item, tabsdata):
        allchildren = item.GetChildren()
        for eachkid in allchildren:
            myid = eachkid.GetName()
            if myid[0] == '1' and myid[1] == '0':
                tab = int(myid[1])
                ctrl = myid[5:]
                data = tabsdata[0]['gnrlsets']
                if ctrl == '011':
                    eachkid.SetValue(str(data['noiselimitstetig']))
                elif ctrl == '012':
                    eachkid.SetValue(str(data['noiselimitdiskret']))
                elif ctrl == '021':
                    if data['zeroshareGs'] in ('False', False):
                        eachkid.SetValue(False)
                    else:
                        eachkid.SetValue(True)
                elif ctrl == '031':
                    eachkid.SetItems(data['baseoptions'])
                    eachkid.SetStringSelection(str(data['readset']))
            elif myid[0] == '1' and int(myid[1]) > 0:
                tab = int(myid[1])
                attnr = int(myid[3:5])
                attrow = tabsdata[tab]['attxdata'][attnr]
                ctrl = myid[5:]
                if ctrl == '010' or ctrl == '110':
                    eachkid.SetValue(attrow['name'])
                elif ctrl == '020':
                    eachkid.Set(attrow['baseoptions'])
                    for i, eachcheck in enumerate(attrow['base']):
                        eachkid.Check(i, eachcheck)
                elif ctrl == '031':
                    eachkid.SetStringSelection(attrow['disttype'])
                elif ctrl == '032':
                    eachkid.SetStringSelection(str(attrow['options']))
                elif ctrl == '040':
                    if attnr == tabsdata[tab]['gridnr']:
                        eachkid.SetValue(True)
                    else:
                        eachkid.SetValue(False)
                elif ctrl == '120':
                    eachkid.SetValue(str(attrow['share']))
                elif ctrl == '131':
                    eachkid.SetStringSelection(str(attrow['units']))
                elif ctrl == '140':
                    if attnr == tabsdata[tab]['grpnr']:
                        eachkid.SetValue(True)
                    else:
                        eachkid.SetValue(False)
                else:
                    pass
            elif myid == None:
                break
            else:
                self.updatecontrols(eachkid, tabsdata)

    def updategrids(self, item, tabsdata):
        try:
            allchildren = item.GetChildren()
            for eachkid in allchildren:
                myid = eachkid.GetName()
                if myid[2] == '2' or myid[2] == '5':
                    tab = int(myid[1])
                    if myid[2] == '2':
                        attnr = tabsdata[tab]['gridnr']
                        newconditions = (tabsdata[tab]['attxdata']
                                         [attnr]['conditions'])
                    elif myid[2] == '5':
                        maxunits = 0
                        for eachclstr in tabsdata[tab]['attxdata']:
                            if eachclstr['units'] > maxunits:
                                maxunits = eachclstr['units']
                                attnr = eachclstr['nr']
                        griddata = eachkid.setupgriddata(tabsdata[tab], attnr)
                        newconditions = griddata
                    labels = eachkid.makelabels(tabsdata[tab], attnr)
                    tabledata = (labels, newconditions)
                    containerpanel = eachkid.GetParent()
                    eachkid.tablebase.ResetView(containerpanel,
                                                tabledata)
                elif myid == None:
                    break
                else:
                    self.updategrids(eachkid, tabsdata)
        except:
            pass
            
    def getoldconditions(self, item):
        try:
            allchildren = item.GetChildren()
            for eachkid in allchildren:
                myid = eachkid.GetName()
                if myid[2] == '2' or myid[2] == '5':
                    self.oldconditions[myid] = eachkid.tablebase.data
                elif myid == None:
                    break
                else:
                    self.getoldconditions(eachkid)
        except:
            print 'getoldconditions - Unexpected error:', sys.exc_info()
        return self.oldconditions


class AttDefTabs(wx.Notebook):
    def __init__(self, parent, id, tabsdata):
        wx.Notebook.__init__(self, parent, id, style=wx.BK_DEFAULT)
        self.createnotebook(tabsdata)
        
    def createnotebook(self, tabsdata):
        self.tabG = TabG(self, tabsdata[0])
        self.AddPage(self.tabG, 'General Settings')
        self.tab0 = Tab(self, tabsdata[1])
        self.AddPage(self.tab0, 'Dependency 1. Order')
        self.tab1 = Tab(self, tabsdata[2])
        self.AddPage(self.tab1, '2. Order')
        self.tab2 = Tab(self, tabsdata[3])
        self.AddPage(self.tab2, '3. Order')
        self.tab3 = Tab(self, tabsdata[4])
        self.AddPage(self.tab3, '4. Order')


class TabG(wx.Panel):
    def __init__(self, parent, tab):
        wx.Panel.__init__(self, parent)
        self.createTab(tab)

    def createTab(self, tab):
        self.gpanel = GPanel(self, tab)

    def change_tab(self, tab):
        pass


class GPanel(wx.Panel):
    def __init__(self, parent, tab):
        wx.Panel.__init__(self, parent, -1)
        self.gbsizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.GPcontent(tab)
        self.SetSizer(self.gbsizer)
        self.Fit()
        self.SetAutoLayout(1)

    def GPcontent(self, tab):
        ehandlers = tab['ehandlers']
        tabnr = tab['tabnr']
        gnrlsets = tab['gnrlsets']
        x1 = 7      #typ
        nr = 1      #nr
        x2 = 0      #ctrl-nr
        myid = self.makemyid(tabnr, x1, nr, x2)
        self.options = ['']
        for b in gnrlsets['baseoptions']:
            self.options.append(str(b))

        self.request00 = wx.Button(self, -1, 'OK', name=str(myid))
        self.gbsizer.Add(self.request00, pos=(0,0), flag=wx.BU_EXACTFIT)
        self.request00.Bind(wx.EVT_BUTTON, ehandlers['bOK'])
        self.request01 = wx.StaticText(self, -1,
                                       'Limit stochastic noise:')
        self.gbsizer.Add(self.request01,
                         pos=(1,0), span=(1,3), flag=wx.EXPAND)
        x1 = 6
        x2 = 11
        myid = self.makemyid(tabnr, x1, nr, x2)
        self.request011 = wx.StaticText(self, -1,
                                        'for continuous distributions below N size: ')
        self.answer011 = wx.TextCtrl(self, -1,
                                     str(gnrlsets['noiselimitstetig']),
                                     size=(125, -1), name=str(myid))
        self.answer011.Bind(wx.EVT_TEXT, ehandlers['number'])
        self.gbsizer.Add(self.request011,
                         pos=(2,0), span=(1,2), flag=wx.EXPAND)
        self.gbsizer.Add(self.answer011,
                         pos=(2,3), flag=wx.EXPAND)
        x2 = 12
        myid = self.makemyid(tabnr, x1, nr, x2)
        self.request012 = wx.StaticText(self, -1,
                                        'for discrete distributions below N size: ')
        self.answer012 = wx.TextCtrl(self, -1,
                                     str(gnrlsets['noiselimitdiskret']),
                                     size=(125, -1), name=str(myid))
        self.answer012.Bind(wx.EVT_TEXT, ehandlers['number'])
        self.gbsizer.Add(self.request012,
                         pos=(3,0), span=(1,2), flag=wx.EXPAND)
        self.gbsizer.Add(self.answer012,
                         pos=(3,3), flag=wx.EXPAND)

        self.request02 = wx.StaticText(self, -1,
                                       'Creation of groups:')
        self.gbsizer.Add(self.request02,
                         pos=(4,0), span=(1,3), flag=wx.EXPAND)
        x2 = 21
        myid = self.makemyid(tabnr, x1, nr, x2)
        self.answer021 = wx.CheckBox(self, -1, 'allow groups with 0% share',
                                     name=str(myid))
        self.answer021.Bind(wx.EVT_CHECKBOX, ehandlers['check'])
        self.gbsizer.Add(self.answer021,
                         pos=(5,0), flag=wx.EXPAND)
        x2 = 31
        myid = self.makemyid(tabnr, x1, nr, x2)
        self.request031 = wx.StaticText(self, -1,
                                        'Zone-specific settings:')
        self.answer031 = wx.Choice(self, -1,
                                   wx.DefaultPosition, wx.DefaultSize,
                                   self.options, name=str(myid))
        self.answer031.Bind(wx.EVT_CHOICE, ehandlers['readset'])
        self.gbsizer.Add(self.request031,
                         pos=(6,0), flag=wx.EXPAND)
        self.gbsizer.Add(self.answer031,
                         pos=(6,3), flag=wx.EXPAND)

    def makemyid(self, tabnr, x1, nr, x2):
        return (10000000 + tabnr*1000000 + x1*100000 + nr*1000 + x2)


class Tab(wx.SplitterWindow):
    def __init__(self, parent, tab):
        wx.SplitterWindow.__init__(self, parent,
                                   style=wx.SP_LIVE_UPDATE)
        self.createTab(tab)

    def createTab(self, tab):
        self.upperpanel = UpperPanel(self, tab)
        self.lowerpanel = LowerPanel(self, tab)
        self.SetMinimumPaneSize(50)
        self.SplitHorizontally(self.upperpanel,
                               self.lowerpanel, -150)
        self.SetSashGravity(0.5)

    def change_tab(self, tab):
        self.upperpanel.UPupdate(tab)

    def makemyid(self, tabnr, x1, nr, x2):
        return (10000000 + tabnr*1000000 + x1*100000 + nr*1000 + x2)


class UpperPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, tab):
        scrolled.ScrolledPanel.__init__(self, parent,-1)
        self.tabnr = tab['tabnr']
        upperbox = wx.StaticBox(self, -1)
        self.upperboxsizer = wx.StaticBoxSizer(upperbox, wx.VERTICAL)
        self.content = self.UPcontent(tab)
        self.upperboxsizer.Add(self.content, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.SetSizer(self.upperboxsizer)
        self.SetAutoLayout(1)
        self.SetupScrolling()

    def UPcontent(self, tab):
        rowboxsizer = wx.BoxSizer(wx.VERTICAL)
        controlsizer = self.UPcontrol(tab)
        rowboxsizer.Add(controlsizer, 0, wx.ALL, 1)
        self.attrowssizer = wx.BoxSizer(wx.VERTICAL)
        self.UPattrows(tab)
        rowboxsizer.Add(self.attrowssizer, 0, wx.ALL, 1)
        return rowboxsizer
        
    def UPcontrol(self, tab):
        requests = tab['requests']
        self.request001 = wx.StaticText(self, -1, requests[0])
        if tab['tabtype'] == 'A':
            x1 = 1
        elif tab['tabtype'] == 'B':
            x1 = 4
        myid = self.makemyid(self.tabnr, x1, 0, 1)
        ehandlers = tab['ehandlers']
        self.answer001 = wx.Button(self, -1, '+',
                                   style=wx.BU_EXACTFIT, name=str(myid))
        self.answer001.Bind(wx.EVT_BUTTON, ehandlers['b+'])
        self.answer002 = wx.Button(self, -1, '-',
                                   style=wx.BU_EXACTFIT, name=str(myid+1))
        self.answer002.Bind(wx.EVT_BUTTON, ehandlers['b-'])
        self.answer003 = wx.Button(self, -1, 'OK',
                                   style=wx.BU_EXACTFIT, name=str(myid+2))
        self.answer003.Bind(wx.EVT_BUTTON, ehandlers['bOK'])
        controlsizer = wx.BoxSizer(wx.HORIZONTAL)
        controlsizer.Add(self.request001, 0,
                     wx.FIXED_MINSIZE | wx.ALIGN_LEFT | wx.ALL, 3)
        controlsizer.Add(self.answer001, 0, wx.ALIGN_LEFT)
        controlsizer.Add(self.answer002, 0, wx.ALIGN_LEFT)
        controlsizer.Add(self.answer003, 0, wx.ALIGN_LEFT)
        return controlsizer

    def UPattrows(self, tab):
        self.attrows = []
        ehandlers = tab['ehandlers']
        if tab['tabtype'] == 'A':
            x1 = 0
        elif tab['tabtype'] == 'B':
            x1 = 3
        for nr, eachatt in enumerate(tab['attxdata']):
            myid = self.makemyid(self.tabnr, x1, nr, 0)
            if tab['tabtype'] == 'A':
                row = Tab_A_attrow(self, ehandlers, nr, eachatt, myid)
            elif tab['tabtype'] == 'B':
                row = Tab_B_attrow(self, ehandlers, nr, eachatt, myid)
            self.attrows.append(row)        
        for eachrow in self.attrows:
            self.attrowssizer.Add(eachrow, 1,
                                  wx.FIXED_MINSIZE | wx.EXPAND | wx.ALL, 3)

    def makemyid(self, tabnr, x1, nr, x2):
        return (10000000 + tabnr*1000000 + x1*100000 + nr*1000 + x2)

    def UPupdate(self, tab):
        self.attrowssizer.Clear(deleteWindows=True)
        self.UPattrows(tab)
        self.Layout()

    def OnText(self, event):    # necessary?
        event.Skip()


class Tab_A_attrow(wx.Panel):
    def __init__(self, parent, ehandlers, nr, attrow, myid):
        wx.Panel.__init__(self, parent,
                          style=wx.BORDER_SIMPLE)
        self.SetAutoLayout(True)
        self.rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.create_attrow(ehandlers, nr, attrow, myid)
        self.SetSizer(self.rowsizer)
        self.rowsizer.Fit(self)

    def create_attrow(self, ehandlers, nr, attrow, myid):
        self.distributions = ['continuous', 'discrete']
        self.options = []
        for i in range(1, 21):
            self.options.append(str(i))
        self.request01 = wx.StaticText(self, -1, 'Name: ')
        self.answer01 = wx.TextCtrl(self, -1, attrow['name'],
                                    size=(125, -1), name=str(myid+10))
        self.answer01.Bind(wx.EVT_TEXT, ehandlers['name'])
        self.request02 = wx.StaticText(self, -1, 'Base: ')
        self.answer02 = wx.CheckListBox(self, -1, size=(150,100),
                                        choices=attrow['baseoptions'],
                                        name=str(myid+20))
        self.answer02.Bind(wx.EVT_CHECKLISTBOX , ehandlers['selectbase'])
        self.request031 = wx.StaticText(self, -1, 'Distribution: ')
        self.answer031 = wx.RadioBox(self, -1, '',
                                     wx.DefaultPosition, wx.DefaultSize,
                                     self.distributions, 1, wx.RA_SPECIFY_ROWS,
                                     name=str(myid+31))
        self.answer031.Bind(wx.EVT_RADIOBOX, ehandlers['selectdist'])
        self.request032 = wx.StaticText(self, -1, 'Options')
        self.answer032 = wx.Choice(self, -1,
                                   wx.DefaultPosition, wx.DefaultSize,
                                   self.options, name=str(myid+32))
        self.answer032.Bind(wx.EVT_CHOICE, ehandlers['selectopt'])
        self.showgrid = wx.RadioButton(self, -1,
                                       'Show distribution / Attribute -',
                                       wx.DefaultPosition, wx.DefaultSize,
                                       name=str(myid+40), style=wx.RB_SINGLE)
        self.showgrid.Bind(wx.EVT_RADIOBUTTON, ehandlers['selectgrid'])
        self.rowsizer.Add(self.request01, 0,
                     wx.FIXED_MINSIZE | wx.ALIGN_LEFT | wx.ALL, 4)
        self.rowsizer.Add(self.answer01, 0,
                     wx.ALIGN_LEFT | wx.ALL, 1)
        self.rowsizer.Add((10,10))
        self.rowsizer.Add(self.request02, 0,
                     wx.FIXED_MINSIZE | wx.ALIGN_LEFT | wx.ALL, 4)
        self.rowsizer.Add(self.answer02, 0,
                     wx.EXPAND | wx.ALL, 1)
        self.rowsizer.Add((10,10))
        self.rowsizer.Add(self.request031, 0,
                     wx.FIXED_MINSIZE | wx.ALIGN_LEFT | wx.ALL, 4)
        self.rowsizer.Add(self.answer031, 0,
                     wx.ALIGN_LEFT | wx.ALL, 1)
        self.rowsizer.Add((10,10))
        self.rowsizer.Add(self.answer032, 0,
                     wx.ALIGN_TOP | wx.ALL, 1)
        self.rowsizer.Add(self.request032, 0,
                     wx.FIXED_MINSIZE | wx.ALIGN_LEFT | wx.ALL, 4)
        self.rowsizer.Add((10,10))
        self.rowsizer.Add(self.showgrid, 0,
                     wx.ALIGN_LEFT | wx.ALL, 4)


class Tab_B_attrow(wx.Panel):
    def __init__(self, parent, ehandlers, nr, attrow, myid):
        wx.Panel.__init__(self, parent,
                          style=wx.BORDER_SIMPLE)
        self.SetAutoLayout(True)
        self.rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.create_attrow(ehandlers, nr, attrow, myid)
        self.SetSizer(self.rowsizer)
        self.rowsizer.Fit(self)

    def create_attrow(self, ehandlers, nr, attrow, myid):
        self.units = []
        for i in range(1, 10):
            self.units.append(str(i))
        self.request11 = wx.StaticText(self, -1, 'Name: ')
        self.answer11 = wx.TextCtrl(self, -1, attrow['name'],
                                    size=(125, -1), name=str(myid+110))
        self.answer11.Bind(wx.EVT_TEXT, ehandlers['name'])
        self.request12 = wx.StaticText(self, -1, 'Share: ')
        self.answer12 = wx.TextCtrl(self, -1, str(attrow['share']),
                                    size=(125, -1), name=str(myid+120))
        self.answer12.Bind(wx.EVT_TEXT , ehandlers['share'])
        self.request131 = wx.StaticText(self, -1, 'Units')
        self.answer131 = wx.Choice(self, -1,
                                   wx.DefaultPosition, wx.DefaultSize,
                                   self.units, name=str(myid+131))
        self.answer131.Bind(wx.EVT_CHOICE, ehandlers['selectunits'])
        self.showgrid = wx.RadioButton(self, -1, 'Group -',
                                       wx.DefaultPosition, wx.DefaultSize,
                                       name=str(myid+140), style=wx.RB_SINGLE)
        self.showgrid.Bind(wx.EVT_RADIOBUTTON, ehandlers['selectgrp'])
        self.rowsizer.Add(self.request11, 0,
                     wx.FIXED_MINSIZE | wx.ALIGN_LEFT | wx.ALL, 4)
        self.rowsizer.Add(self.answer11, 0,
                     wx.ALIGN_LEFT | wx.ALL, 1)
        self.rowsizer.Add((10,10))
        self.rowsizer.Add(self.request12, 0,
                     wx.FIXED_MINSIZE | wx.ALIGN_LEFT | wx.ALL, 4)
        self.rowsizer.Add(self.answer12, 0,
                     wx.EXPAND | wx.ALL, 1)
        self.rowsizer.Add((10,10))
        self.rowsizer.Add(self.request131, 0,
                     wx.FIXED_MINSIZE | wx.ALIGN_LEFT | wx.ALL, 4)
        self.rowsizer.Add(self.answer131, 0,
                     wx.ALIGN_LEFT | wx.ALL, 1)
        self.rowsizer.Add((10,10))
        self.rowsizer.Add(self.showgrid, 0,
                     wx.ALIGN_LEFT | wx.ALL, 4)


class LowerPanel(wx.Panel):
    def __init__(self, parent, tab):
        wx.Panel.__init__(self, parent)
        self.tabnr = tab['tabnr']
        requests = tab['requests']
        attnr = 0
        lowerbox = wx.StaticBox(self, -1, requests[1])
        lowerboxsizer = wx.StaticBoxSizer(lowerbox, wx.VERTICAL)
        content = self.lowerpanelcontent(tab, attnr)
        lowerboxsizer.Add(content, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.SetSizer(lowerboxsizer)

    def lowerpanelcontent(self, tab, attnr):
        ehandlers = tab['ehandlers']
        if tab['tabtype'] == 'A':
            x1 = 2
        elif tab['tabtype'] == 'B':
            x1 = 5
        myid = self.makemyid(self.tabnr, x1, attnr, 0)
        attgrid = ConditionsGrid(self, tab, attnr, myid)
        attgrid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, ehandlers['gridentry'])
        lowerbox = wx.BoxSizer(wx.HORIZONTAL)
        lowerbox.Add(attgrid, 0, wx.ALL, 2)
        return lowerbox

    def makemyid(self, tabnr, x1, nr, x2):
        return (10000000 + tabnr*1000000 + x1*100000 + nr*1000 + x2)


class ConditionsGrid(grd.Grid):
    def __init__(self, parent, tab, nr, myid):
        grd.Grid.__init__(self, parent, -1, name=str(myid))
        griddata = self.setupgriddata(tab, nr)
        attdata = tab['attxdata'][nr]
        self.rowlabels = self.makelabels(tab, nr)[0]
        self.collabels = self.makelabels(tab, nr)[1]
        self.tablebase = PGTableBase(griddata,
                                     self.rowlabels, self.collabels)
        self.SetTable(self.tablebase)
        self.SetRowLabelSize(100)
        self.formattable(griddata)

    def setupgriddata(self, tab, nr):
        if tab['tabtype'] == 'A':
            griddata = tab['attxdata'][nr]['conditions']
        elif tab['tabtype'] == 'B':
            griddata = []
            for eachclstr in tab['attxdata']:
                griddata.append(eachclstr['conditions'])
            griddata = map(lambda *row:
                           [elem or '-' for elem in row],
                           *griddata)
        return griddata

    def formattable(self, griddata):
        colour0 = wx.WHITE
        colour1 = wx.Colour(165, 228, 225, 255)
        colour2 = wx.LIGHT_GREY
        for row, eachrow in enumerate(griddata):
            for col, eachvalue in enumerate(eachrow):
                if row == 0:
                    self.SetCellBackgroundColour(row, col, colour1)
                elif eachvalue == '-':
                    self.SetReadOnly(row, col, True)
                    self.SetCellBackgroundColour(row, col, colour2)
                else:
                    self.SetReadOnly(row, col, False)
                    self.SetCellBackgroundColour(row, col, colour0)

    def makelabels(self, tab, nr):
        attdata = tab['attxdata'][nr]
        if tab['tabtype'] == 'A':
            rowlabels = [attdata['name']]
            for nr, eachatt in enumerate(attdata['base']):
                if eachatt == True:
                    rowlabels.append(attdata['baseoptions'][nr])
            collabels = []
            for col in range(int(attdata['options'])):
                collabels.append(col)
        elif tab['tabtype'] == 'B':
            rows = 0
            for eachclstr in tab['attxdata']:
                rows = max(rows, int(eachclstr['units']))
            rowlabels = ['Share:']
            for row in range(rows):
                rowlabels.append(str(row + 1))
            collabels = []
            for eachclstr in tab['attxdata']:
                collabels.append(eachclstr['name'])
        return rowlabels, collabels


class PGTableBase(grd.PyGridTableBase):
    def __init__(self, cellvalues, rowLabels=None, colLabels=None):
        grd.PyGridTableBase.__init__(self)
        self.data = cellvalues
        self.rowLabels = rowLabels
        self.colLabels = colLabels
        self.currentRows = self.GetNumberRows()
        self.currentCols = self.GetNumberCols()

    def ResetView(self, containerpanel, tabledata):
        """Trim/extend the control's rows and update all values"""
        self.data = tabledata[1]
        self.rowLabels = tabledata[0][0]
        self.colLabels = tabledata[0][1]
        self.getGrid().BeginBatch()
        for current, new, delmsg, addmsg in [ 
            (self.currentRows, self.GetNumberRows(),
             grd.GRIDTABLE_NOTIFY_ROWS_DELETED,
             grd.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self.currentCols, self.GetNumberCols(),
             grd.GRIDTABLE_NOTIFY_COLS_DELETED,
             grd.GRIDTABLE_NOTIFY_COLS_APPENDED)
            ]:
            if new < current:
                msg = grd.GridTableMessage(
                    self,
                    delmsg,
                    new,    # position
                    current-new,
                )
                self.getGrid().ProcessTableMessage(msg)
            elif new > current:
                msg = grd.GridTableMessage(
                    self,
                    addmsg,
                    new-current
                )
                self.getGrid().ProcessTableMessage(msg)
        self.UpdateValues()
        self.getGrid().EndBatch()
        lblsize = self.getLblsize(self.rowLabels)
        self.getGrid().SetRowLabelSize(lblsize)
        self.currentRows = self.GetNumberRows()
        self.currentCols = self.GetNumberCols()
        self.getGrid().formattable(self.data)
        h,w = containerpanel.GetSize()
        containerpanel.SetSize((h+1, w))
        containerpanel.SetSize((h, w))
        containerpanel.Update()

    def getLblsize(self, lblist):
        size = 50
        for eachlbl in lblist:
            size = max(size, (8 * len(eachlbl)))
        return size

    def getGrid(self):
        return self.GetView()

    def UpdateValues(self):
        """Update all displayed values"""
        msg = grd.GridTableMessage(self,
                                   grd.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.getGrid().ProcessTableMessage(msg)
 
    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data[0])

    def GetColLabelValue(self, col):
        if self.colLabels:
            return self.colLabels[col]
        
    def GetRowLabelValue(self, row):
        if self.rowLabels:
            try:
                return self.rowLabels[row]
            except:
                return None
        
    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        return str(self.data[row][col])

    def SetValue(self, row, col, value):
        newrow = list(self.data[row])
        newrow[col] = str(value)
        self.data[row] = newrow


class ProtocolFrame(wx.Frame):  
    def __init__(self, parent, settings):
        wx.Frame.__init__(self, parent, -1, title='Settings',
                pos=wx.DefaultPosition, size=wx.DefaultSize,
                style=wx.DEFAULT_FRAME_STYLE & ~(wx.CLOSE_BOX))
        self.ctrl = wx.TextCtrl(self, -1, settings,
                size=wx.DefaultSize,
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        
    def SetLog(self, settings):
        self.ctrl.SetValue(settings)


class FileDlg(wx.FileDialog):
    def __init__(self, parent, title, path, extension, style):
        wx.FileDialog.__init__(self, None, title, path, '', extension, style)
        if self.ShowModal() == wx.ID_OK:
            self.OnChoice()

    def OnChoice(self):
        return self.GetDirectory(), self.GetFilename()
        self.Destroy()


class DirDlg(wx.DirDialog):
    def __init__(self, parent, title, path):
        wx.DirDialog.__init__(self, None, title, path)
        if self.ShowModal() == wx.ID_OK:
            self.OnChoice()

    def OnChoice(self):
        return self.GetPath()
        self.Destroy()


class ProgressView(wx.ProgressDialog):
    def __init__(self, parent, p_info):
        wx.ProgressDialog.__init__(self, title='Synthesis',
                                   message=p_info['title'],
                                   maximum=1000, parent=parent,
                                   style=wx.PD_ELAPSED_TIME |
                                   wx.PD_ESTIMATED_TIME |
                                   wx.PD_REMAINING_TIME |
                                   wx.PD_SMOOTH |
                                   wx.STAY_ON_TOP |
                                   wx.PD_CAN_ABORT)

    def PVupdate(self, p_info):
        return self.Update(p_info['value'], p_info['title'])


class AboutWindow(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, title='About',
                    pos=wx.DefaultPosition, size=wx.DefaultSize,
                    style=wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX)
            self.ctrl = wx.TextCtrl(self, -1, '',
                    size=wx.DefaultSize,
                    style=wx.TE_MULTILINE | wx.TE_READONLY)
            licence = (' r88_Structurama is a program developed for \
the synthesis of populations and other structures based on aggregate \
data available in DBF and statistical information on underlying \
distributions from any source.\n\n (C) 2012 Timotheus Andreas Klein \
- Tim.Klein(at)gmx.de\n\n This program is free software: you can \
redistribute it and/or modify it under the terms of the GNU General \
Public License as published by the Free Software Foundation, either \
version 3 of the License, or (at your option) any later version.\n\n\
 This program is distributed in the hope that it will be useful, but \
WITHOUT ANY WARRANTY; without even the implied warranty of \
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU \
General Public License for more details.\n\n You should have received \
a copy of the GNU General Public License along with this program.  If \
not, see <http://www.gnu.org/licenses/>.')
            self.ctrl.SetValue(licence)
