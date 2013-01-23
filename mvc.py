#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# 
# MVC Part r88_structurama
#
# Model and Controller Part of r88_structurama, which try to maintain
# the integrity of input data and structural data synthesized.
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

import os
import numpy
import wx
import random
import dbf
import gui
import sqlitecontrol


class Observable:
    def __init__(self, initialValue=None):
        self.data = initialValue
        self.callbacks = {}

    def addCallback(self, func):
        self.callbacks[func] = 1

    def delCallback(self, func):
        del self.callback[func]

    def _docallbacks(self):
        for func in self.callbacks:
            func(self.data)

    def set_(self, data):
        self.data = data
        self._docallbacks()

    def get(self):
        return self.data

    def unset(self):
        self.data = None


class Model:
    def __init__(self):
        self.settings = [[self.defaultGnrl(0, 0)],
                         [self.defaultAtt(1, 0)],
                         [self.defaultAtt(2, 0)],
                         [self.defaultGrp(3, 0)],
                         [self.defaultAtt(4, 0)]]
        self.mySettings = Observable(self.settings)
        self.p_info = {'title': '*',
                       'value': 0}
        self.myPinfo = Observable(self.p_info)
        self.myLog = Observable('')
        self.dbfdirname = ''
        self.dbfilename = ''
        self.DBdirname = ''
        self.DBfilename = ''

    def defaultGnrl(self, order, nr):
        return {'order': order,
                'nr': nr,
                'noiselimitstetig': 0,
                'noiselimitdiskret': 0,
                'zeroshareGs': False,
                'baseoptions': ['?', '??'],
                'readset': ''}

    def defaultAtt(self, order, nr):
        return {'order': order,
                'nr': nr,
                'name': 'new_attribute',
                'baseoptions': ['?', '??'],
                'base': [False, False],
                'disttype': 'continuous',
                'options': '2',
                'conditions': [['from', 'to']],
                }

    def defaultGrp(self, order, nr):
        return {'order': order,
                'nr': nr,
                'name': 'Other',
                'share': '0',
                'units': '1',
                'conditions': ['0%', '1:'],
                }

    def getDbfCols(self):
        try:
            dbf = self.dbfdirname + '\\' + self.dbfilename
            dbfcols = self.readfromDbf(dbf, 'dbfcols')
            if len(dbfcols) > 0:
                return dbfcols
            else:
                return ['None']
        except:
            return ['?', '??']

    def _updateNumbers(self, order):
        for nr, eachitem in enumerate(self.settings[order]):
            eachitem['nr'] = nr

    def _updateBaseOptions(self):
        baseoptions = []
        baseoptions.extend(self.getDbfCols())
        for order, eachorder in enumerate(self.settings):
            if order == 1:
                for eachatt in eachorder:
                    eachatt['baseoptions'] = list(baseoptions)
            elif order == 2:
                for eachatt in self.settings[order-1]:
                    if eachatt['disttype'] == 'continuous':
                        baseoptions.append(eachatt['name'])
                    else:
                        for eachoption in eachatt['conditions'][0]:
                            baseoptions.append(
                                eachatt['name'] + '.' +
                                str(eachoption))
                for eachatt in self.settings[order]:
                    eachatt['baseoptions'] = list(baseoptions)
            elif order == 3:
                groups = []
                for eachgrp in eachorder:
                    groups.append(eachgrp['name'])
            elif order == 4:
                for eachatt in eachorder:
                    eachatt['baseoptions'] = list(groups)
        
    def _updateBase(self):
        for eachorder in self.settings[1:]:
            if len(eachorder) > 0:
                if eachorder[0].has_key('baseoptions'):
                    baseoptions = len(eachorder[0]['baseoptions'])
                    for eachatt in eachorder:
                        base = range(baseoptions)
                        for nr, eachbase in enumerate(base):
                            try:
                                base[nr] = eachatt['base'][nr]
                            except:
                                base[nr] = False
                        eachatt['base'] = base

    def _updateShares(self):
        for eachorder in self.settings:
            if len(eachorder) > 0:
                if eachorder[0].has_key('share'):
                    total = 0
                    for eachgrp in eachorder:
                        total += float(eachgrp['share'])
                    for nr, eachgrp in enumerate(eachorder):
                        share = float(eachgrp['share'])
                        if total > 0:
                            sharepc = str(round(100 * share / total, 3))
                        else:
                            sharepc = '0.000'
                        sharepc = sharepc[0:(sharepc.index('.') + 4)] + '%'
                        eachgrp['conditions'][0] = sharepc

    def selectDbf(self, dirfile):
        self.dbfdirname = dirfile[0]
        self.dbfilename = dirfile[1]
        dbf = dirfile[0] + '\\' + dirfile[1]
        self.dbfcols = self.readfromDbf(dbf, 'dbfcols')
        self.changeMySettings()
        self.info = '$DBF: \n* DBF\n' + dirfile[0] + '\n' + dirfile[1] + '\n'
        self.changeLog(self.info)

    def selectDB(self, dirfile):
        self.DBdirname = dirfile[0]
        self.DBfilename = dirfile[1]
        self.info = '$RES: \n* RES\n' + dirfile[0] + '\n' + dirfile[1] + '\n'
        self.changeLog(self.info)
        
    def addattribute(self, order):
        order = int(order)
        nr = 0
        self.settings[order].append(self.defaultAtt(order, nr))
        self._updateNumbers(order)
        self._updateBaseOptions()
        self._updateBase()

    def addgroup(self, order):
        order = int(order)
        nr = 0
        self.settings[order].append(self.defaultGrp(order, nr))
        self._updateNumbers(order)

    def removeattribute(self, order, nr):
        order = int(order)
        nr = int(nr)
        trash = self.settings[order].pop(nr)
        self._updateNumbers(order)
        self._updateBaseOptions()
        self._updateBase()
        
    def removegroup(self, order, nr):
        order = int(order)
        nr = int(nr)
        trash = self.settings[order].pop(nr)
        self._updateNumbers(order)
        
    def readFile(self, dirfile1str):
        f = open(dirfile1str, 'r')
        return f.read().decode('iso-8859-1')

    def saveFile(self, dirfile1str, info):
        info = info.encode('iso-8859-1')
        f = open(dirfile1str, 'w')
        f.write(info)

    def changeLog(self, info):
        self.myLog.set_(self.myLog.get() + info)

    def replaceLog(self, newlog):
        self.myLog.set_(newlog)

    def addtoLog(self, order, item):
        newinfo = ('$' + str(order) + '.' + str(item['nr']) + '\n'
                   '* Order.Nr\n')
        for eachkey in item.keys():
            try:
                newinfo += (eachkey + ':\t' + item[eachkey] + '\n')
            except:
                newinfo += (eachkey + ':\t' + str(item[eachkey]) + '\n')
        self.changeLog(newinfo)

    def Log_to_Sets(self, newlog):
        self.settings = [[self.defaultGnrl(0, 0)],
                         [self.defaultAtt(1, 0)],
                         [self.defaultAtt(2, 0)],
                         [self.defaultGrp(3, 0)],
                         [self.defaultAtt(4, 0)]]
        for info in newlog.split('$'):
            if len(info) > 2:
                infolines = info.splitlines(True)
                self.readLog(infolines)

    def readLog(self, infolines):
        if 'DBF' in infolines[0]:
            self.dbfdirname = infolines[2].rstrip('\n')
            self.dbfilename = infolines[3].rstrip('\n')
        elif 'RES' in infolines[0]:
            self.DBdirname = infolines[2].rstrip('\n')
            self.DBfilename = infolines[3].rstrip('\n')
        elif infolines[0][0].isalnum() == True:
            logitem = {}
            logitem['order'] = int(infolines[0].partition('.')[0])
            logitem['nr'] = int(infolines[0].partition('.')[2])
            trash = infolines.pop(0)
            for eachline in infolines:
                if '*' in eachline:
                    pass
                elif ('conditions:\t' in eachline or
                      'base' in eachline):
                    key = eachline.partition(':\t')[0]
                    value = eval(
                        eachline.partition(':\t')[2].rstrip('\n'))
                    logitem[key] = value
                else:
                    key = eachline.partition(':\t')[0]
                    value = eachline.partition(':\t')[2].rstrip('\n')
                    logitem[key] = value
            self.enterLogitem(logitem)

    def enterLogitem(self, logitem):
        for eachentry in logitem.keys():
            try:
                logitem[eachentry] = int(logitem[eachentry])
            except:
                pass
        order = logitem['order']
        while len(self.settings) < (order + 1):
            self.settings.insert(order, [])
        nr = logitem['nr']
        while len(self.settings[order]) < (nr + 1):
            self.settings[order].insert(nr, {})
        logitemdata = self.getlogitemdata(logitem)
        self.settings[order][nr] = logitemdata
        
    def getlogitemdata(self, logitem):
        LIdata = {}
        LIdata['order'] = logitem['order']
        LIdata['nr'] = logitem['nr']
        for LIk, LIv in logitem.iteritems():
            if LIv == 'True':
                LIv = True
            elif LIv == 'False':
                LIv = False
            LIdata[LIk] = LIv
        return LIdata
    
    def saveLog(self, dirfile1str):
        log = self.tidyLog()
        self.replaceLog(log)
        self.saveFile(dirfile1str, log)
        
    def tidyLog(self):
        self.settings = self.mySettings.get()
        newlog = ('$DBF: \n* DBF\n' +
                  self.dbfdirname + '\n' +
                  self.dbfilename + '\n' +
                  '$RES: \n* Results Database File\n' +
                  self.DBdirname + '\n' +
                  self.DBfilename + '\n')
        self.replaceLog(newlog)
        for nr, eachorder in enumerate(self.settings):
            for eachitem in eachorder:
                self.addtoLog(nr, eachitem)
        return self.myLog.get()

    def openLog(self, dirfile1str):
        newlog = self.readFile(dirfile1str)
        self.setsdir = dirfile1str[:dirfile1str.rfind('/')]
        self.setsdir = self.setsdir.strip('/')
        self.replaceLog(newlog)
        self.Log_to_Sets(newlog)
        self.changeMySettings()

    def readfromDbf(self, dbfname, what):
        if '.dbf' in dbfname:
            dbfile = dbf.Table(dbfname)
            if what == 'dbfcols':
                return dbfile.field_names
            if what == 'table':
                allrecords = []
                for record in dbfile:
                    recordlist = []
                    for eachfield in dbfile.field_names:
                        recordlist.append(record[eachfield])
                    allrecords.append(recordlist)
                return dbfile.field_names, allrecords
            else:
                allrecords = []
                for eachrec in dbfile:
                    allrecords.append(eachrec[what])
                return allrecords
                
    def changeMySettings(self):
        self._updateBaseOptions()
        self._updateBase()
        self._updateShares()
        self.mySettings.set_(self.settings)

    def maxCellNr(self, dbfname):
        dbfile = dbf.Table(dbfname)
        idstr = dbfile.field_names[0]
        allnumbers = self.readfromDbf(dbfname, idstr)
        return max(allnumbers)

    def populate(self):
        p_info = self.p_info
        myLog = self.myLog.get()
        self.Log_to_Sets(myLog)
        mySettings = self.mySettings.get()
        if mySettings[0][0]['zeroshareGs'] in ('False', False):
            mySettings[0][0]['zeroshareGs'] = False
        else:
            mySettings[0][0]['zeroshareGs'] = True
        self.myusualSettings = mySettings
        self.mydbfdirname = self.dbfdirname
        self.mydbfilename = self.dbfilename
        self.myDBdirname = self.DBdirname
        self.myDBfilename = self.DBfilename
        DB = self.DBdirname + '\\' + self.DBfilename
        dbfdirfilename = self.dbfdirname + '\\' + self.dbfilename
        try:
            os.remove(DB)
        except:
            pass
        table = self.readfromDbf(dbfdirfilename, 'table')
        dbfinput = {}
        digits = len(str(self.maxCellNr(dbfdirfilename)))
        for nr, eachrow in enumerate(table[1]):
            t_pc = min(nr * 1000 / len(table[1]), 999)
            p_info['value'] = t_pc
            for nr, eachcol in enumerate(table[0]):
                dbfinput[eachcol] = eachrow[nr]
            cellsets = self.determinesets(mySettings, dbfinput)
            self.dbfdirname = self.mydbfdirname
            self.dbfilename = self.mydbfilename
            self.DBdirname = self.myDBdirname
            self.DBfilename = self.myDBfilename
            zoneNr = str(eachrow[0])
            while len(zoneNr) < digits:
                zoneNr = '0' + zoneNr
            tname = 'Zone_' + zoneNr
            p_info['title'] = tname
            self.progressupdate(p_info)
            zone_pop = pop_cell(cellsets, dbfinput, DB, tname)
            p_info['title'] += ' - 1. O.'
            self.progressupdate(p_info)
            zone_pop.first_order()
            p_info['title'] += ' - 2. O.'
            self.progressupdate(p_info)            
            zone_pop.second_order()
            p_info['title'] += ' - 3. O.'
            self.progressupdate(p_info)
            zone_pop.group()
            p_info['title'] += ' - 4. O.'
            self.progressupdate(p_info)
            zone_pop.fourth_order()
            p_info['title'] = 'Count'
            self.progressupdate(p_info)
            zone_pop.AttCount(tname)
            zone_pop.GrpCount(tname)
            zone_pop.GACount(tname)
            p_info['title'] = 'Intersections'
            self.progressupdate(p_info)
            zone_pop.finalKVcheck(tname)
            zone_pop.delGATable(tname)
            p_info['title'] = 'Done'
            self.progressupdate(p_info)
            self.mySettings.set_(self.myusualSettings)
            if 'Cancel' in self.p_info['title']:
                break
        t_pc = 1000
        p_info['value'] = t_pc
        self.progressupdate(p_info)

    def progressupdate(self, myPinfo):
        self.myPinfo.set_(myPinfo)

    def determinesets(self, mySettings, dbfinput):
        readset = mySettings[0][0]['readset']
        if readset == '' or dbfinput[readset] == '':
            cellsets = mySettings
        else:
            dirfile1str = self.setsdir + '//' + dbfinput[readset]
            if '.set' not in dirfile1str:
                dirfile1str += '.set'
            self.openLog(dirfile1str)
            cellsets = self.mySettings.get()
        return cellsets

class pop_cell:
    def __init__(self, settings, dbfinput, DB, tname):
        self.db = sqlitecontrol.sqlctrl(DB)
##        self.db.executesql('PRAGMA synchronous = OFF')
        self.settings = settings
        self.settingsstr = str(settings)
        self.dbfinput = dbfinput
        self.tname = tname
        self.columns = ['PID']
        datatypes = ['INTEGER']
        self.db.createtable(self.tname, self.columns, datatypes)
        self.db.createindex(self.tname, 'PID')
        if 'Count' not in self.db.gettablenames():
            self.db.createtable('Count', ['Zone'], ['TEXT'])
        if self.db.countentries('Count',
                                {'Zone':
                                 ' = "' + tname + '"'})[0][0] == 0:
            self.db.insertrow('Count', ['Zone'], [tname])
        random.seed()
        
    def first_order(self):
        FO_settings = self.settings[1]
        PID = 0
        self.db.insertcol(self.tname, 'gisbase', 'TEXT')
        self.columns.append('gisbase')
        inittable = []
        for eachbase in self.listbases(FO_settings):
            persons = self.dbfinput[eachbase]
            for eachperson in range(persons):
                data = [PID, eachbase]
                inittable.append(data)
                self.db.insertrow(self.tname, self.columns, data)
                PID += 1
        for eachatt in FO_settings:
            self.attribute(eachatt)
        self.db.finish()

    def second_order(self):
        SO_settings = self.settings[2]
        for eachatt in SO_settings:
            self.attribute(eachatt)
        self.db.finish()

    def group(self):
        zeroShGs = self.settings[0][0]['zeroshareGs']
        Gdef = self.settings[3]
        target = self.targetdistribution(Gdef)
        actual = numpy.zeros(len(target))
        self.db.insertcol(self.tname, 'GID', 'INTEGER')
        self.db.createindex(self.tname, 'GID')
        self.db.insertcol(self.tname, 'GTYP', 'TEXT')
        self.db.createindex(self.tname, 'GTYP')
        GID = 0
        allPID = self.db.countentries(self.tname, {})[0][0]
        remaining = self.pop_left()
        while remaining > 0:
            oldGtypes = []
            Gcomplete = False
            createPID = False
            while Gcomplete == False:
                if len(oldGtypes) == len(target):
                    if zeroShGs == False:
                        pop_before = allPID
                        self.db.deleterow(self.tname,
                                          {'GID': 'IS NULL'})
                        self.copygroups(pop_before, target, Gdef)
                        break
                    oldGtypes = []
                newGtype = self.nextGtype(Gdef, oldGtypes,
                                          target, actual)
                newG = self.buildG(Gdef, newGtype)
                if newG[0] == True:
                    Gcomplete = True
                    self.enterGinDB(GID, newGtype, newG[1])
                    actual = self.actualdistribution(Gdef)
                    GID += 1
                else:
                    oldGtypes.append(str(newGtype))
                remaining = self.pop_left()
        self.db.finish()

    def fourth_order(self):
        FO_settings = self.settings[4]
        realtname = self.tname
        self.tname = 'tmp_' + self.tname
        self.createGAT(realtname)
        for eachatt in FO_settings:
            self.attribute(eachatt)
        self.transferGAvalues(realtname)
        self.db.finish()
        self.tname = realtname

    def createGAT(self, tname):
        self.db.createtable(self.tname,
                            ['PID', 'gisbase'],
                            ['INTEGER', 'TEXT'])
        GIDcol = self.db.getcol(tname, 'GID', {})
        GTYPcol = self.db.getcol(tname, 'GTYP', {})
        GAdata = map(None, *[GIDcol, GTYPcol])
        GAdata.sort()
        lastGID = None
        for eachrec in GAdata:
            if eachrec[0][0] <> lastGID:
                values = str(eachrec[0][0]), eachrec[1][0]
                self.db.insertrow(self.tname,
                                  ['PID', 'gisbase'],
                                  values)
            lastGID = eachrec[0][0]

    def transferGAvalues(self, tname):
        GAnames = self.db.getcolnames(self.tname)
        newcols = []
        for eachcol in GAnames[3:]:
            self.db.insertcol(tname, eachcol, 'TEXT')
            newcols.append(eachcol)
        GAvalues = self.db.gettable(self.tname)
        for rownr, eachrow in enumerate(GAvalues):
            GID = eachrow[1]
            Wdict = {'GID': ' = "' + str(GID)+ '"'}
            for colnr, eachcol in enumerate(newcols):
                self.db.changeentry(tname, eachcol,
                                    eachrow[3:][colnr], Wdict)

    def finalKVcheck(self, tname):
        self.KVCTname = 'Intersections'
        tablenames = self.db.gettablenames()
        if self.KVCTname not in tablenames:
            cols = ['Zone']
            datatypes = ['TEXT']
            self.db.createtable(self.KVCTname, cols, datatypes)
        zone_col = self.db.getcol(self.KVCTname, 'Zone', {})
        if [tname] not in zone_col:
            self.db.insertrow(self.KVCTname, ['Zone'], [tname])
        for eachatt in self.settings[1]:
            if eachatt['disttype'] == 'discrete':
                self.getattKV(eachatt, tname)
        for eachatt in self.settings[2]:
            if eachatt['disttype'] == 'discrete':
                self.getattKV(eachatt, tname)
        self.getgrpKV(tname)
        for eachatt in self.settings[4]:
            if eachatt['disttype'] == 'discrete':
                self.getattKV(eachatt, 'tmp_' + tname)
        self.db.finish()

    def getgrpKV(self, tname):
        if 'GTYP' not in self.db.getcolnames(self.KVCTname):
            self.db.insertcol(self.KVCTname, 'GTYP', 'FLOAT')
        Gdef = self.settings[3]
        target = self.targetdistribution(Gdef)
        actual = self.actualdistribution(Gdef)
        KV = self.KV_calc(target, actual)
        KVdict = {'Zone': ' = "' + str(tname)+ '"'}
        self.db.changeentry(self.KVCTname, 'GTYP', KV, KVdict)

    def getattKV(self, eachatt, tname):
        for nr, eachbase in enumerate(self.listbase(eachatt)):
            eachbase = eachbase.encode('utf-8')
            colname = eachbase + '.' + eachatt['name'].encode('utf-8')
            BSAdef = self.basespec_attdef(eachatt, nr,
                                          eachbase)
            classes = BSAdef['options']
            target = BSAdef['conditions']
            target = self.norm_hist(target)
            if colname not in self.db.getcolnames(self.KVCTname):
                self.db.insertcol(self.KVCTname, colname, 'FLOAT')
            values = self.db.selectentries(tname,
                                           [BSAdef['colname']],
                                           BSAdef['wheredict'])
            actual = self.getdistribution(classes, values)
            actual = self.norm_hist(actual)
            KV = self.KV_calc(target, actual)
            maintname = tname.lstrip('tmp_')
            KVdict = {'Zone': ' = "' + str(maintname)+ '"'}
            self.db.changeentry(self.KVCTname,
                                colname, KV,
                                KVdict)

    def AttCount(self, tname):
        for eachO in self.settings[1:3]:
            for eachAtt in eachO:
                if eachAtt['disttype'] == 'discrete':
                    for eachOption in eachAtt['conditions'][0]:
                        acolname = (eachAtt['name'] + '.' +
                                    eachOption)
                        if acolname not in self.db.getcolnames('Count'):
                            self.db.insertcol('Count',
                                              acolname, 'INTEGER')
                        count = self.countAttSpec(tname,
                                                  eachAtt['name'],
                                                  eachOption)
                        self.db.changeentry('Count', acolname, count,
                                            {'Zone':
                                             ' ="' + tname + '"'})

    def countAttSpec(self, tname, attname, option):
        WDict = {attname: ' = "' + option + '"'}
        return self.db.countentries(tname, WDict)[0][0]
        
    def GrpCount(self, tname):
        for eachG in self.settings[3]:
            gcolname = ('G.' + eachG['name']).encode('utf-8')
            if gcolname not in self.db.getcolnames('Count'):
                self.db.insertcol('Count', gcolname, 'INTEGER')
            count = self.countGrpSpec(tname, eachG['name'])
            self.db.changeentry('Count', gcolname, count,
                                {'Zone':
                                 ' ="' + tname + '"'})

    def countGrpSpec(self, tname, GAname):
        GATname = 'tmp_' + tname
        WDict = {'gisbase': (' = "' + GAname + '"').encode('utf-8')}
        return self.db.countentries(GATname, WDict)[0][0]
        
    def GACount(self, tname):
        for eachGA in self.settings[4]:
            gacolname = ('GA.' + eachGA['name']).encode('utf-8')
            if gacolname not in self.db.getcolnames('Count'):
                self.db.insertcol('Count', gacolname, 'INTEGER')
            count = self.countGrpSpec(tname, eachGA['name'])
            self.db.changeentry('Count', gacolname, count,
                                {'Zone':
                                 ' ="' + tname + '"'})

    def delGATable(self, tname):            
        try: self.db.droptable('tmp_' + tname)
        except: pass

    def copygroups(self, pop_before, target, Gdef):
        pop_after = self.db.countentries(self.tname, {})[0][0]
        oldGtypes = []
        while pop_after <> pop_before:
            pop_after = self.db.countentries(self.tname, {})[0][0]
            actual = self.actualdistribution(Gdef)
            tryGT = self.nextGtype(Gdef, oldGtypes, target, actual)
            CWdict = {'"GID"': ' IS NOT NULL',
                      '"GTYP"': ' = "' + str(tryGT) + '"'}
            tryGs = self.db.selectentries(self.tname, ['GID'],
                                          CWdict)
            tryG = random.sample(tryGs, 1)[0][0]
            Gvol = self.db.countentries(self.tname,
                                        {'GID': ' = "' + str(tryG) + '"'})[0][0]
            if pop_after + Gvol <= pop_before:
                self.copyGID(tryG)
            else:
                oldGtypes.append(str(tryGT))

    def copyGID(self, GID):
        oldPs = self.db.selectentries(self.tname, '*',
                                      {'GID': ' = "' + str(GID) + '"'})
        startPID = max(self.db.selectentries(self.tname,
                                             ['PID'], {}))[0] + 1
        startid = max(self.db.selectentries(self.tname,
                                            ['id'], {}))[0] + 1
        newCID = max(self.db.selectentries(self.tname,
                                           ['GID'], {}))[0] + 1
        cols = self.db.getcolnames(self.tname)
        for eacholdP in oldPs:
            eacholdP[0] = startid
            eacholdP[1] = startPID
            eacholdP[-2] = newCID
            startid += 1
            startPID += 1
            self.db.insertrow(self.tname, cols, eacholdP)
        
    def buildG(self, Gdef, newGtype):
        complete = True
        for eachCtype in Gdef:
            if eachCtype['name'] == newGtype:
                GTdef = eachCtype['conditions'][1:]
                break
        PIDs = []
        Gdict = {}
        Unr = 1
        for eachunit in GTdef:
            if eachunit == '-':
                break
            else:
                newunit = self.gatherunit(Gdict, PIDs, eachunit)
                if newunit[0] == True:
                    PIDs.extend(newunit[1])
                    if len(newunit[1]) > 0:
                        Gdict[Unr] = newunit[1][0]
                else:
                    complete = False
                    break
            Unr += 1
        return complete, PIDs

    def gatherunit(self, Gdict, PIDs, Udef):
        complete = False
        UPs = self.readUdef(Gdict, Udef)
        Ucount = UPs[0]
        UWdict = UPs[1]
        for nr, eachPID in enumerate(PIDs):
            key = nr * ' ' + '"PID"'
            value = ' <> ' + str(eachPID[0])
            UWdict[key] = value
        availablePIDs = self.getavailablePIDs(UWdict)
        PIDs = availablePIDs[:Ucount]
        if len(availablePIDs) >= Ucount:
            PIDs = random.sample(availablePIDs, Ucount)
            complete = True
        return complete, PIDs

    def getavailablePIDs(self, UWdict):
        PIDs = self.db.selectentries(self.tname, ['PID'], UWdict)
        return PIDs

    def nextGtype(self, Gdef, oldGtypes, target, actual):
        diffs = []
        zeroShGs = self.settings[0][0]['zeroshareGs']
        for nr, eachclass in enumerate(Gdef):
            if eachclass['name'] not in oldGtypes:
                if (float(eachclass['share']) > 0.0 or zeroShGs == True):
                    diffs.append([[actual[nr] - target[nr]],
                                  eachclass['name']])
        while len(diffs) == 0:
            GTdef = random.sample(Gdef, 1)[0]
            Gtype = GTdef['name']
            if (float(GTdef['share']) > 0.0 or zeroShGs == True):
                diffs.append([1, Gtype])
        diffs.sort()
        Gtype = diffs[0][1]
        return Gtype

    def readUdef(self, Gdict, Udef):
        Unumberstr = Udef.partition(':')[0]
        if '..' in Unumberstr:
            Unumber = random.randint(
                int(Unumberstr.partition('..')[0]),
                int(Unumberstr.partition('..')[2]))
        else:
            Unumber = int(Unumberstr)
        UWdict = {'GID': 'IS NULL'}
        for nr, eachcond in enumerate(
            Udef.partition(':')[2].split(';')):
            whereclause = str(eachcond)
            whereclause = whereclause.replace('<', '"<"')
            whereclause = whereclause.replace('>', '">"')
            whereclause = whereclause.replace('=', '"="')
            whereclause = whereclause.replace('""', '')
            if '"' in whereclause:
                key = '"' + whereclause.split('"')[0] + '"' + nr * ' '
                valuestr = whereclause.split('"')[2]
                operator = whereclause.split('"')[1]
            else:
                key = '"id"'
                valuestr = '0'
                operator = '>='
            if '#' in valuestr:
                valuestr = self.getrelcon(Gdict, valuestr, operator)
            else:
                if type(valuestr) == str:
                    valuestr = '"' + valuestr + '"'
                else:
                    pass
            UWdict[key] = operator + ' ' + valuestr
        return Unumber, UWdict

    def getrelcon(self, Gdict, valuestr, operator):
        RUnr = int(valuestr.partition('.')[0].replace('#', ''))
        RUatt = self.clipright(valuestr, '+-/*')
        RUattname = RUatt.partition('.')[2]
        RUPIDs = Gdict[RUnr]
        RUattvalue = self.Uattvalue(RUattname, RUPIDs)[0]
        if (type(RUattvalue[0]) == int or
            type(RUattvalue[0]) == float):
            if RUatt <> valuestr:
                RUop = valuestr.partition('.')[2][len(RUattname)]
                mod = float(
                    valuestr.partition('.')[2][(len(RUattname) + 1):])
            else:
                RUop = None
            if operator == '<':
                RUattvalue = min(RUattvalue)
            elif operator == '>':
                RUattvalue = max(RUattvalue)
            elif operator == '=':
                RUattvalue = sum(RUattvalue) / len(RUattvalue)
            if RUop == '-':
                RUattvalue = RUattvalue - mod
            elif RUop == '+':
                RUattvalue = RUattvalue + mod
            elif RUop == '/':
                RUattvalue = RUattvalue / mod
            elif RUop == '*':
                RUattvalue = sum(RUattvalue) / len(RUattvalue)
                RUattvalue = RUattvalue * mod
            else:
                pass
            valuestr = str(RUattvalue)
        else:
            valuestr = '"' + RUattvalue[0].decode('utf-8') + '"'
            # takes the first among several
        return valuestr

    def Uattvalue(self, attname, RUPIDs):
        rupidstr = 'IN ' + str(tuple(RUPIDs))
        rupidstr = rupidstr.replace('[', '')
        rupidstr = rupidstr.replace(']', '')
        wheredict = {'PID': rupidstr}
        values = self.db.selectentries(self.tname,
                                       [attname],
                                       wheredict)
        return values

    def pop_left(self):
        wheredict = {'GID': 'IS NULL'}
        remaining = self.db.countentries(self.tname, wheredict)[0][0]
        return remaining

    def targetdistribution(self, Gdef):
        target = []
        for eachgrp in Gdef:
            target.append(eachgrp['share'])
        target = self.norm_hist(target)
        return target

    def actualdistribution(self, Gdef):
        actual = []
        for eachgrp in Gdef:
            wheredict = {'GTYP': '= "' + eachgrp['name'] + '"'}
            count = self.countclasses(self.db.selectentries(
                self.tname, ['GID'], wheredict))
            actual.append(count)
        if sum(actual) > 0:
            actual = self.norm_hist(actual)
        return actual

    def clipright(self, string, seps):
        for eachsep in seps:
            if string.find(eachsep) > -1:
                string = string.split(eachsep)[0]
        return string

    def enterGinDB(self, GID, Gtype, PIDs):
        for eachPID in PIDs:
            wheredict = {'PID': '= ' + str(eachPID[0])}
            self.db.changeentry(self.tname, 'GID', GID, wheredict)
            self.db.changeentry(self.tname, 'GTYP', Gtype, wheredict)

    def listbases(self, items):
        baseslist = []
        for eachitem in items:
            baselist = self.listbase(eachitem)
            for eachbase in baselist:
                if eachbase in baseslist:
                    pass
                else:
                    baseslist.append(eachbase)
        return baseslist

    def listbase(self, item):
        baselist = []
        baseoptions = item['baseoptions']
        base = item['base']
        for nr, eachbase in enumerate(base):
            if eachbase == True:
                baselist.append(baseoptions[nr])
        return baselist

    def basespec_attdef(self, attdef, nr, eachbase):
        BSAdef = {}
        BSAdef['colname'] = attdef['name'].encode('utf-8')
        BSAdef['options'] = attdef['conditions'][0]
        BSAdef['conditions'] = attdef['conditions'][nr+1]
        BSAdef['whichcols'] = ['PID', 'gisbase', attdef['name']]
        BSAdef['wheredict'] = {}
        eachbase = eachbase.encode('utf-8')
        if eachbase.partition('.')[0] in self.db.getcolnames(self.tname):
            basename = eachbase.partition('.')[0]
            basevalue = '="' + str(eachbase.partition('.')[2]) + '"'
            BSAdef['wheredict'][basename] = basevalue
        else:
            BSAdef['wheredict']['gisbase'] = '="' + str(eachbase) + '"'
        return BSAdef
            
    def attribute(self, attdef):
        for nr, eachbase in enumerate(self.listbase(attdef)):
            BSAdef = self.basespec_attdef(attdef, nr, eachbase)
            if attdef['disttype'] == 'continuous':
                newrecs = self.att_stetig(BSAdef)
            else:
                BSAdef['conditions'] = self.norm_hist(BSAdef['conditions'])
                newrecs = self.att_diskret(BSAdef)
            if self.settingsstr.count(BSAdef['colname']) > 1:
               self.db.createindex(self.tname, BSAdef['colname']) 
            for nr, eachrec in enumerate(newrecs):
                wheredict = {'PID': '="' + str(eachrec[0]) + '"'}
                newvalue = eachrec[2]
                try:
                    self.db.changeentry(self.tname, BSAdef['colname'],
                                        newvalue, wheredict)
                except:
                    self.db.changeentry(self.tname, BSAdef['colname'],
                                        newvalue[0], wheredict)

    def att_stetig(self, BSAdef):
        maxsize = self.settings[0][0]['noiselimitstetig']
        if BSAdef['colname'] not in self.db.getcolnames(self.tname):
            self.db.insertcol(self.tname, BSAdef['colname'], 'FLOAT')
        relevantrecs = self.db.selectentries(self.tname,
                                             BSAdef['whichcols'],
                                             BSAdef['wheredict'])
        recsize = len(relevantrecs)
        samplerange = 10 ** len(str(recsize))
        if recsize > maxsize:
            values = random.sample(xrange(samplerange), recsize)
        else:
            step = samplerange / recsize
            values = range((step / 2), samplerange, step)
        fvalue = float(BSAdef['conditions'][0])
        tvalue = float(BSAdef['conditions'][1])
        span = tvalue - fvalue
        newrecs = []
        for nr, eachrec in enumerate(relevantrecs):
            eachrec = list(eachrec)
            eachrec[2] = ((float(BSAdef['conditions'][0]) +
                           span * values[nr] / samplerange))
            newrecs.append(eachrec)
        return newrecs
            
    def att_diskret(self, BSAdef):
##        for eachoption in BSAdef['options']:
##            acolname = BSAdef['colname'] + '.' + eachoption
##            if acolname not in self.db.getcolnames('Count'):
##                self.db.insertcol('Count', acolname, 'TEXT')
        maxsize = self.settings[0][0]['noiselimitdiskret']
        cum_cond = self.h_cumulative(BSAdef['conditions'])
        maxloops = len(cum_cond)
        newrecs = []
        if BSAdef['colname'] not in self.db.getcolnames(self.tname):
            self.db.insertcol(self.tname, BSAdef['colname'], 'TEXT')
        relevantrecs = self.db.selectentries(self.tname,
                                             BSAdef['whichcols'],
                                             BSAdef['wheredict'])
        recsize = len(relevantrecs)
        for nr, eachrec in enumerate(relevantrecs):
            eachrec = list(eachrec)
            eachrec[2] = self.mc_diskret(BSAdef['options'],
                                         cum_cond)
            if (len(newrecs) > 1 and recsize < maxsize):
                improved = self.check_KV(BSAdef,
                                         newrecs, eachrec[2])
                loops = 0
                while (loops < maxloops and
                       improved == False):
                    eachrec[2] = self.mc_diskret(BSAdef['options'],
                                                 cum_cond)
                    improved = self.check_KV(BSAdef,
                                             newrecs, eachrec[2])
                    loops += 1
            newrecs.append(eachrec)
        return newrecs

    def check_KV(self, BSAdef, newrecs, newrec):
        classes = BSAdef['options']
        target = BSAdef['conditions']
        oldvalues = []
        for eachrec in newrecs:
            oldvalues.append(eachrec[2])
        newvalues = list(oldvalues)
        newvalues.append(newrec)
        actualold = self.getdistribution(classes, oldvalues)
        actualnew = self.getdistribution(classes, newvalues)
        improved = self.KV_improved(target, actualold, actualnew)
        return improved

    def getdistribution(self, classes, values):
        distribution = numpy.zeros(len(classes))
        for eachvalue in values:
            for nr, eachclass in enumerate(classes):
                if type(eachvalue) == list or type(eachvalue) == tuple:
                    eachvalue = eachvalue[0]
                if eachvalue == eachclass:
                    distribution[nr] += 1
                    break
        distribution = distribution / sum(distribution)
        return distribution

    def KV_improved(self, target, actualold, actualnew):
        improved = True
        KVold = self.KV_calc(target, actualold)
        KVnew = self.KV_calc(target, actualnew)
        if KVnew < KVold:
            improved = False
        return improved

    def KV_calc(self, target, actual):
        KV = 0
        for nr, eachclass in enumerate(target):
            KV += min(eachclass, actual[nr])
        return KV

    def mc_diskret(self, options, cum_cond):
        mc_value = random.uniform(0, max(cum_cond))
        for nr, eachvalue in enumerate(cum_cond):
            if mc_value < eachvalue:
                value = options[nr]
                break
            else:
                value = random.sample(options, 1)
        return value

    def countclasses(self, values):
        classes = 0
        knownvalues = []
        for eachv in values:
            if eachv in knownvalues:
                pass
            else:
                knownvalues.append(eachv)
                classes += 1
        return classes

    def h_cumulative(self, histogram):
        cumdist = [float(histogram[0])]
        for nr, eachclass in enumerate(histogram[1:]):
            eachclass = float('0' + str(eachclass).strip('na'))
            cumdist.append(max(cumdist) + eachclass)
        return cumdist

    def c_histogram(self, cumdist):
        histogram = []
        for nr, eachclass in enumerate(cumdist):
            eachclass = float('0' + str(eachclass).strip('na'))
            if nr > 0:
                histogram.append(eachclass -
                                 float(cumdist[nr-1]))
            else:
                histogram.append(eachclass)
        return histogram

    def norm_hist(self, histo):
        histonew = []
        sumh = 0.0
        for eachclass in histo:
            eachclass = float('0' + str(eachclass).strip('na'))
            sumh += eachclass
        if sumh == 0:
            sumh = 1
        for eachclass in histo:
            eachclass = float('0' + str(eachclass).strip('na'))
            histonew.append(eachclass / sumh)
        return histonew

    def norm_cumd(self, cumd):
        sumc = 0
        for eachclass in cumd:
            eachclass = float('0' + str(eachclass).strip('na'))
            eachclass = eachclass + sumc
            sumc += eachclass
        if sumc == 0:
            sumc = 1
        for eachclass in cumd:
            eachclass = float('0' + str(eachclass).strip('na'))
            eachclass = eachclass / max(cumd)
        return cumd


class Controller:
    def __init__(self, app):
        self.model = Model()
        self.settings = self.model.mySettings.get()
        self.dbfdirname = self.model.dbfdirname
        self.DBdirname = self.model.DBdirname
        self.tabsdata = [self.defaultTab_G(0),
                         self.defaultTab_A(1),
                         self.defaultTab_A(2),
                         self.defaultTab_B(3),
                         self.defaultTab_A(4)]
        self.updateTabsdata()
        self.view = gui.AttDefFrame(
            self.menuData,
            self.tabsdata)
        self.model.myLog.addCallback(self.myLogChanged)
        self.model.mySettings.addCallback(self.mySettingsChanged)
        self.model.myPinfo.addCallback(self.progressMade)
        self.view.Show()
        self.protocolWindow = False
        self.progressView = False
        self.aboutWindow = False

    def menuData(self):
        return (('&File',
                 ('n', '&Open settings', '', self.OnLogOpen),
                 ('n', '&Save settings', '', self.OnLogSave),
                 ('n', '', '', ''),
                 ('n', '&Select DBF', '', self.OnDbf),
                 ('n', '', '', ''),
                 ('n', '&Select Results Database', '', self.OnResultDB),
                 ('n', '', '', ''),
                 ('n', '&Exit', '', self.OnCloseWindow),
                 ),
                ('&Synthesize',
                 ('n', '&Start', '', self.OnStart),
                 ),
                ('&Info',
                 ('c', '&Protocol Window', '', self.OnProtocol),
                 ('n', '', '', ''),
                 ('n', '&About', '', self.OnAbout)
                 ))

    def defaultTab_G(self, tab):
        return {
            'tabnr': tab,
            'tabtype': 'G',
            'gnrlsets': [],
            'ehandlers': self.tab_G_events()
            }

    def tab_G_events(self):
        return {
            'bOK': self.On_OK,
            'number': self.OnNumber,
            'check': self.OnCheck,
            'readset': self.OnReadSet
            }

    def defaultTab_A(self, tab):
        return {
            'tabnr': tab,
            'tabtype': 'A',
            'requests': ['Attribute',
                         'Distribution selected attribute'],
            'attxdata': [],
            'gridnr': 0,
            'ehandlers': self.tab_A_events()
            }

    def tab_A_events(self):
        return {
            'b+': self.OnPlus,
            'b-': self.OnMinus,
            'bOK': self.On_OK,
            'name': self.OnText,
            'selectbase': self.OnBase,
            'selectdist': self.OnDists,
            'selectopt': self.OnOpts,
            'selectgrid': self.OnGrid,
            'gridentry': self.OnGridEntry
            }

    def defaultTab_B(self, tab):
        return {
            'tabnr': tab,
            'tabtype': 'B',
            'requests': ['Groups',
                         'Definition'],
            'attxdata': [],
            'grpnr': 0,
            'conditions': [['A'],['unit_1']],
            'ehandlers': self.tab_B_events()
            }
    
    def tab_B_events(self):
        return {
            'b+': self.OnPlus,
            'b-': self.OnMinus,
            'bOK': self.On_OK,
            'name': self.OnText,
            'share': self.OnShare,
            'selectunits': self.OnUnits,
            'selectgrp': self.OnSelect,
            'gridentry': self.OnGridEntry
            }

    def updateTabsdata(self):
        self.tabsdata[0]['gnrlsets'] = self.settings[0][0]
        for nr, eachorder in enumerate(self.settings[1:]):
            self.tabsdata[nr+1]['attxdata'] = eachorder

    def OnAbout(self, event):
        if self.aboutWindow == False: self.aboutWindow = True
        else: self.aboutWindow = False
        if self.aboutWindow:
            self.about = gui.AboutWindow(self.view)
            self.about.Show()
        else:
            self.about.Destroy()

    def OnReadSet(self, event):
        readset = event.GetEventObject().GetStringSelection()
        self.settings[0][0]['readset'] = readset

    def OnShare(self, event):
        share = event.GetEventObject().GetValue()
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        nr = myid[2]
        self.settings[order][nr]['share'] = share

    def OnUnits(self, event):
        units = event.GetEventObject().GetStringSelection()
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        nr = myid[2]
        self.settings[order][nr]['units'] = units
        newconditions = []
        for i in range(int(units) + 1):
            if i < len(self.settings[order][nr]['conditions']):
                newcond = str(self.settings[order][nr]['conditions'][i])
                if newcond == '-':
                    newcond = '<>'
                newconditions.append(newcond)
            else:
                newconditions.append('<>')
        self.settings[order][nr]['conditions'] = newconditions

    def OnSelect(self, event):
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        nr = myid[2]
        self.tabsdata[order]['grpnr'] = nr
        self.changeMySettings()
    
    def OnPlus(self, event):
        myid = self.readmyid(event.GetEventObject().GetName())
        tab = myid[0]
        if myid[1] == 1:
            self.model.addattribute(tab)
        elif myid[1] == 4:
            self.model.addgroup(tab)
        self.settings = self.model.settings
        self.updateTabsdata()
        self.rebuildTabs(self.tabsdata)

    def OnMinus(self, event):
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        typ = myid[1]
        if typ == 1:
            nr = self.tabsdata[order]['gridnr']
            self.model.removeattribute(order, nr)
        elif typ == 4:
            nr = self.tabsdata[order]['grpnr']
            if nr > 0:
                self.model.removegroup(order, nr)
        self.settings = self.model.settings
        self.updateTabsdata()
        self.rebuildTabs(self.tabsdata)

    def On_OK(self, event):
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        for eachitem in self.settings[order]:
            self.model.addtoLog(order, eachitem)
        if myid[1] == 1:
            for nr in range(len(self.settings[order])):
                self.updateGrid(order, nr)
        elif myid[1] == 4:
            nr = 0
            self.updateGrid(order, nr)
        self.changeMySettings()
        self.changeGrids(self.tabsdata)

    def changeMySettings(self):
        self.model.settings = self.settings
        self.model.changeMySettings()

    def OnNumber(self, event):
        number = event.GetEventObject().GetValue()
        myid = self.readmyid(event.GetEventObject().GetName())
        nr = myid[2]
        x2 = myid[3]
        if nr == 1 and len(number) > 0:
            if x2 == 11:
                self.settings[0][0]['noiselimitstetig'] = int(number)
            elif x2 == 12:
                self.settings[0][0]['noiselimitdiskret'] = int(number)
        else:
            pass

    def OnCheck(self, event):
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        if myid[1] in [6, 7]:
            checked = event.GetEventObject().GetValue()
            self.settings[order][0]['zeroshareGs'] = checked
        else:
            pass

    def OnText(self, event):
        name = event.GetEventObject().GetValue()
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        nr = myid[2]
        self.settings[order][nr]['name'] = name
        
    def OnGrid(self, event):
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        nr = myid[2]
        self.tabsdata[order]['gridnr'] = nr
        self.updateGrid(order, nr)
        self.changeGrids(self.tabsdata)

    def OnGridEntry(self, event):
        conditions = self.view.getoldconditions(self.view)
        for eachid in conditions.keys():
            myid = self.readmyid(eachid)
            order = myid[0]
            x1 = myid[1]
            if x1 == 2:
                pass
            elif x1 == 5:
                newconditions = map(lambda *row: list(row),
                                    *conditions[eachid])
                for eachgrp in self.settings[order]:
                    nr = int(eachgrp['nr'])
                    eachgrp['conditions'] = newconditions[nr]
        self.updateTabsdata()

    def updateGrids(self):
        for eachorder in self.settings:
            for eachnr in eachorder:
                order = eachnr['order']
                nr = eachnr['nr']
                self.updateGrid(order, nr)

    def updateGrid(self, order, nr):
        if self.tabsdata[order]['tabtype'] == 'A':
            attdata = self.settings[order][nr]
            disttype = str(attdata['disttype'])
            bases = attdata['base'].count(True)
            options = int(attdata['options'])
            newgrid = self.createnewgrid(bases, options)
            attdata['conditions'] = self.fillnewgrid(
                attdata['conditions'], newgrid, disttype)
        if self.tabsdata[order]['tabtype'] == 'B':
            disttype = 'group'
            newgrid = []
            for eachgrp in self.settings[order]:
                newgrid.append(eachgrp['conditions'])
            newgrid = map(lambda *row:
                           [elem or '-' for elem in row],
                           *newgrid)
        self.changeMySettings()

    def createnewgrid(self, rows, cols):
        newgrid = []
        newrow = range(cols)
        for eachrow in range(rows + 1):
            newgrid.append(list(newrow))
        return newgrid

    def fillnewgrid(self, oldgrid, newgrid, disttype):
        for row, eachrow in enumerate(newgrid):
            for col, eachcol in enumerate(eachrow):
                try:
                    newgrid[row][col] = str(oldgrid[row][col])
                except:
                    newgrid[row][col] = ''
        if disttype == 'continuous':
            newgrid[0] = ['from', 'to']
        return newgrid

    def OnBase(self, event):
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        nr = myid[2]
        baseoptions = self.settings[order][nr]['baseoptions']
        checks = event.GetEventObject().GetChecked()
        for i, eachitem in enumerate(baseoptions):
            if i in checks:
                self.settings[order][nr]['base'][i] = True
            else:
                self.settings[order][nr]['base'][i] = False
        self.changeMySettings()

    def OnDists(self, event):
        disttype = event.GetEventObject().GetStringSelection()
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        nr = myid[2]
        self.settings[order][nr]['disttype'] = disttype
        if disttype == 'continuous':
            self.settings[order][nr]['options'] = '2'
        self.changeMySettings()

    def OnOpts(self, event):
        options = event.GetEventObject().GetStringSelection()
        myid = self.readmyid(event.GetEventObject().GetName())
        order = myid[0]
        nr = myid[2]
        self.settings[order][nr]['options'] = options
        if int(options) > 2:
            self.settings[order][nr]['disttype'] = 'discrete'
        self.changeMySettings()
  
    def readmyid(self, myid):
        order = int(myid[1])
        typ = int(myid[2])
        nr = int(myid[3:5])
        ctrl = int(myid[5:])
        return order, typ, nr, ctrl
        
    def OnDbf(self, event):
        dirfile = gui.FileDlg(self, 'Select DBF', self.dbfdirname, 
                              '*.dbf', wx.OPEN).OnChoice()
        if '.dbf' in str(dirfile):
            self.model.selectDbf(dirfile)
            self.updateGrids()

    def OnResultDB(self, event):
        resultDB = gui.FileDlg(self, 'Select Results Database',
                               self.DBdirname, '*.db', wx.OPEN).OnChoice()
        if '.db' in str(resultDB):
            self.model.selectDB(resultDB)

    def OnLogOpen(self, event):
        dirfile = gui.FileDlg(self, 'Open Settings', self.dbfdirname, 
                              '*.set', wx.OPEN).OnChoice()
        dirfile1str = dirfile[0] + '/' + dirfile[1]
        if len(dirfile[1]) > 0:
            self.model.openLog(dirfile1str)
            self.rebuildTabs(self.tabsdata)

    def OnLogSave(self, event):
        dirfile = gui.FileDlg(self, 'Save Settings', self.dbfdirname, 
                              '*.set', wx.SAVE).OnChoice()
        dirfile1str = dirfile[0] + '/' + dirfile[1]
        if len(dirfile[1]) > 0:
            self.model.saveLog(dirfile1str)
        
    def changeLog(self, info):
        self.model.changeLog(info)

    def replaceLog(self, newlog):
        self.model.replaceLog(newlog)

    def OnProtocol(self, event):
        if self.protocolWindow == False: self.protocolWindow = True
        else: self.protocolWindow = False
        if self.protocolWindow:
            self.protocol = gui.ProtocolFrame(self.view,
                                              self.model.myLog.get())
            self.protocol.Show()
        else:
            self.protocol.Destroy()

    def OnStart(self, event):
        self.p_info = self.model.myPinfo.get()
        self.progress = gui.ProgressView(self.view,
                                         self.p_info)
        self.progress.Show()
        self.model.populate()        

    def myLogChanged(self, log):
        if self.protocolWindow == True:
            self.protocol.SetLog(log)

    def mySettingsChanged(self, settings):
        self.settings = settings
        self.updateTabsdata()
        try:
            self.view.updatecontrols(self.view, self.tabsdata)
        except:        
            self.rebuildTabs(self.tabsdata)

    def progressMade(self, p_info):
        if self.progress.PVupdate(p_info)[0] == False:
            p_info = self.model.myPinfo.get()
            p_info['title'] = 'Cancel'
            self.model.P_info = p_info

    def changeGrids(self, tabsdata):
        self.view.updategrids(self.view, self.tabsdata)
 
    def rebuildTabs(self, tabsdata):
        self.view.attdeftabs.tabG.change_tab(tabsdata[0])
        self.view.attdeftabs.tab0.change_tab(tabsdata[1])
        self.view.attdeftabs.tab1.change_tab(tabsdata[2])
        self.view.attdeftabs.tab2.change_tab(tabsdata[3])
        self.view.attdeftabs.tab3.change_tab(tabsdata[4])

    def OnCloseWindow(self, event):
        if self.protocolWindow:
            self.protocol.Destroy()
        if self.progressView:
            self.progress.Destroy()
        if self.aboutWindow:
            self.about.Destroy()
        self.view.Destroy()
