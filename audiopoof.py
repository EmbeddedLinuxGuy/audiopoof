#!C:/Python25/Python.exe
#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# generated by wxGlade 0.6.3 on Wed Feb 18 17:53:41 2009

from __future__ import with_statement

import wx
import sys
import os
import serial
import pickle
import subprocess
import time
import math

#for rgb2hsv
import colorsys

# local goodness
import TestPanel
import AudioProc


# 
SLIDER_SPEED = 91
SLIDER_THRESH = 92
SLIDER_GROSS = 93

POOFER_INDEX = 300              # for poofer buttons

EXIT_MENU = 50
ABOUT_MENU = 51
LOAD_MENU = 52
SAVE_MENU = 53
FILE_MENU = 54
RESET_MENU = 55
AUDIO_MENU = 56

AUDIO_CB = 71
SERIAL_CB = 73
SEQUENCE_CB = 74
REVERSE_CB = 75

FEATHER_CB = 100 # 100-115
FEATHER_TIMER = 120 # 120-135
MAIN_TIMER = 140
HEARTBEAT = 141

# global constants

NUM_CHANNELS = 4                  # number of spectrographic channels
NUM_OUTCHANS = 4                  # number of output channels


class testFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: testFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        self.sequence = [ "0000000000000000" ]
        self.seq_i = 0
        self.delta = 1
        self.crossing = time.time()
        self.cross_list = [0,0,0,0,0]
        for i in range(5):
            # prepopulate with fake data??
            self.cross_list[i] = self.crossing
        self.interval = 500
        self.cross_cursor = 0
        self.Bind(wx.EVT_CHAR, self.onChar)

        # c99 d100 e101 452 v118 f102 r114 553 b98 h104 y121 654 n110 j106 u117 755
        self.keyMap = {
            99 : 13,
            100 : 14,
            101 : 15,
            52 : 16,
            118 : 9,
            102 : 10,
            114 : 11,
            53 : 12,
            98 : 1,
            104 : 2,
            121 : 3,
            54 : 4,
            110 : 5,
            106 : 6,
            117 : 7,
            55 : 8
            }

        self.heartBeat = wx.Timer(self, id=HEARTBEAT)
        self.Bind(wx.EVT_TIMER, self.onHeartBeat, id=HEARTBEAT)

        self.toBits = wx.Button(self, -1, "Add")
        self.Bind(wx.EVT_BUTTON, self.onToBits, self.toBits)

        self.delButton = wx.Button(self, -1, "Remove")
        self.Bind(wx.EVT_BUTTON, self.onDelete, self.delButton)

        # Menu Bar
        self.menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(LOAD_MENU, "Load", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(SAVE_MENU, "Save", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(RESET_MENU, "Reset", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(AUDIO_MENU, "Input Select", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(EXIT_MENU, "Exit", "", wx.ITEM_NORMAL)
        self.menubar.Append(wxglade_tmp_menu, "File")
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(ABOUT_MENU, "About", "", wx.ITEM_NORMAL)
        self.menubar.Append(wxglade_tmp_menu, "Help")
        self.SetMenuBar(self.menubar)
        # Menu Bar end

        self.statusbar = self.CreateStatusBar(1, 0)
        self.slider_thresh = wx.Slider(self, SLIDER_THRESH, 50, 1, 100, style=wx.SL_VERTICAL|wx.SL_LABELS|wx.SL_INVERSE)
#        self.graphicsPanel = TestPanel.TestPanel(self, -1)
        self.label_audio_cb = wx.StaticText(self, -1, "Audio")
        self.label_serial_cb = wx.StaticText(self, -1, "Run")
        self.label_sequence_cb = wx.StaticText(self, -1, "Step")
        self.label_reverse_cb = wx.StaticText(self, -1, "Reverse")
        
        self.cb_audio = wx.CheckBox(self, AUDIO_CB, "")
        self.cb_serial = wx.CheckBox(self, SERIAL_CB, "")
        self.cb_sequence = wx.CheckBox(self, SEQUENCE_CB, "")
        self.cb_reverse = wx.CheckBox(self, REVERSE_CB, "")
        
        self.gauge_audio = wx.Gauge(self, -1, 100, style=wx.GA_VERTICAL|wx.GA_SMOOTH)
        # this loop creates the  list of poofer buttons
        self.pooferbtnmatrix = []    # array of NUM_OUTCHANS*NUM_CHANNELS butns
        keyNames = [
                     "4", "5", "6", "7",
                     "E", "R", "Y", "U",
                     "D", "F", "H", "J",
                     "C", "V", "B", "N"
                     ]
        self.keyChannel = [
                       16, 12, 4, 8,
                       15, 11, 3, 7,
                       14, 10, 2, 6,
                       13, 9, 1, 5
                        ]
          
        for chan in range(NUM_OUTCHANS*NUM_CHANNELS): 
            sc = wx.Button(self, -1, keyNames[chan])
            #sc = wx.Button(self, -1, "%d" % chan)
            self.Bind(wx.EVT_BUTTON, self.onPooferBtn, sc)
            sc.chan = self.keyChannel[chan]
            sc.SetMinSize((60, -1))
            sc.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 1, ""))
            self.pooferbtnmatrix.append(sc)

        self.defaultBtnColour = sc.GetBackgroundColour()

        
        self.__set_properties()
        self.__do_layout()


 
        self.Bind(wx.EVT_MENU, self.doMenu)
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

        self.Bind(wx.EVT_CHECKBOX, self.onCheckBox, id=AUDIO_CB)
        self.Bind(wx.EVT_CHECKBOX, self.onCheckBox, id=SERIAL_CB)
        self.Bind(wx.EVT_CHECKBOX, self.onReverse, id=REVERSE_CB)
        
        # end wxGlade
        
    def onDelete(self, event):
        sel = self.viewer.GetSelection()
        if sel < 0:
            return
        self.viewer.Delete(sel)
        if sel > 0:
            self.viewer.SetSelection(sel-1)

    def onToBits(self, event):
        string = ""
        for i in range(16):
            if self.cb_feathers[i].GetValue():
                string += "1"
            else:
                string += "0"
        string += "\n"
        n = self.viewer.GetCount()
        self.viewer.Insert(string, n)
        self.viewer.SetSelection(n)

    def __set_properties(self):

        self.storeFlag = 0

        # begin wxGlade: testFrame.__set_properties
        self.SetTitle("FLG AudioPoof!")
        self.SetSize((800, 465))
        self.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.statusbar.SetStatusWidths([-1])

        self.slider_thresh.SetMinSize((-1, -1))
        self.slider_thresh.SetBackgroundColour(wx.Colour(236, 233, 216))
#        self.graphicsPanel.SetMinSize((450,200))
#        self.graphicsPanel.SetBackgroundColour(wx.Colour(221, 221, 221))

    def setValues(self,valDict):
        if len(valDict) < 2:
            return

            
        # We initialize to 50 so don't change
        # XXX: Get rid of unused controls and fix presets
        #self.slider_thresh.SetValue(valDict['offs'])
        self.report("Parameters updated")        


    def getValues(self,valDict):


        valDict['offs'] = self.slider_thresh.GetValue()


        return(valDict)

    def __do_layout(self):

        self.cb_feathers = []
        self.timer_feathers = []
        for i in range(16):
            self.cb_feathers.append(wx.CheckBox(self, FEATHER_CB+i, ""))
            self.timer_feathers.append(wx.Timer(self, FEATHER_TIMER+i))
            self.Bind(wx.EVT_TIMER, self.onPoofTimeout, id=FEATHER_TIMER+i)

        cb_grid = wx.GridSizer(5, 10, 5, 0)

        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[15])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[7])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[14])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[11])
        cb_grid.Add(self.cb_feathers[3])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[6])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)

        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[13])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[10])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[2])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[5])
        cb_grid.Add((2,2), 0, 0, 0)

        cb_grid.Add(self.cb_feathers[12])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[9])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[1])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[4])

        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[8])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add(self.cb_feathers[0])
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)
        cb_grid.Add((2,2), 0, 0, 0)

        # begin wxGlade: testFrame.__do_layout1

        sizer_modecbs = wx.GridSizer(5, 1, 0, 0)
        sizer_orbcbs = wx.GridSizer(6, 1, 0, 0)
        sizer_modelabels = wx.GridSizer(5, 1, 0, 0)

        # Checkbox labels
        sizer_modelabels.Add(self.label_audio_cb, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modelabels.Add(self.label_serial_cb, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modelabels.Add(self.label_sequence_cb, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modelabels.Add(self.label_reverse_cb, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        # Checkboxes
        sizer_modecbs.Add(self.cb_audio, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modecbs.Add(self.cb_serial, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modecbs.Add(self.cb_sequence, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modecbs.Add(self.cb_reverse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        
        # listbox
        self.viewer = wx.ListBox(self, 120, (100, 50), (180, 120),
                                 self.sequence,
                                 wx.LB_SINGLE)
        self.viewer.SetSelection(self.seq_i)

        self.sampleList = os.listdir('seq')
        self.sampleList.remove('.svn')
        self.lb1 = wx.ListBox(self, 60, (100, 50), (90, 120), self.sampleList,
                              wx.LB_SINGLE)
        self.lb1.SetSelection(0)
        self.loadSequence()
        self.Bind(wx.EVT_LISTBOX, self.EvtListBox, self.lb1)

        # for each row in the output array
        sizer_matrix = wx.GridSizer(NUM_OUTCHANS, NUM_CHANNELS, 5, 10)
        for btn in self.pooferbtnmatrix:
            sizer_matrix.Add(btn)

        next_button = wx.Button(self, -1, "Next")
        self.Bind(wx.EVT_BUTTON, self.onNextButton, next_button)

        all_button = wx.Button(self, -1, "All")
        inner_button = wx.Button(self, -1, "Inner")
        outer_button = wx.Button(self, -1, "Outer")
        self.Bind(wx.EVT_BUTTON, self.onAllButton, all_button)
        self.Bind(wx.EVT_BUTTON, self.onInnerButton, inner_button)
        self.Bind(wx.EVT_BUTTON, self.onOuterButton, outer_button)

        sizer_buttons = wx.GridSizer(3, 1, 10, 0)
        sizer_buttons.Add(all_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_buttons.Add(inner_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_buttons.Add(outer_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.slider_speed = wx.Slider(self, SLIDER_SPEED, 500, 20, 500, (0,0), (100, 250), style=wx.SL_VERTICAL|wx.SL_LABELS|wx.SL_INVERSE|wx.EXPAND)
        self.slider_gross = wx.Slider(self, SLIDER_SPEED, 0, 0, 4000, (0,0), (100, 250), style=wx.SL_VERTICAL|wx.SL_LABELS|wx.SL_INVERSE|wx.EXPAND)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.onScroll, id=SLIDER_SPEED)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.onScroll, id=SLIDER_GROSS)

        reload_button = wx.Button(self, -1, "Reload")
        self.Bind(wx.EVT_BUTTON, self.onReload, reload_button)


        self.crossing_label = wx.StaticText(self, -1, "0")
        self.saveButton = wx.Button(self, -1, "Save")
        self.Bind(wx.EVT_BUTTON, self.onSave, self.saveButton)
        self.seqName = wx.TextCtrl(self, -1, "patternName", size=(125, -1))

        sizer_outer = wx.FlexGridSizer(2, 2, 0, 0)

        sizer_left = wx.FlexGridSizer(1, 4, 0, 0)
        sizer_left.Add(self.slider_thresh, 0, wx.EXPAND, 0)
        sizer_left.Add(self.gauge_audio, 0, wx.ALL|wx.EXPAND, 0)
        sizer_left.Add(self.slider_gross, 0, wx.EXPAND, 0)
        sizer_left.Add(self.slider_speed, 0, wx.EXPAND, 0)

        edit_sizer = wx.FlexGridSizer(3, 1, 0, 0)
        edit_sizer.Add(self.toBits)
        edit_sizer.Add(self.saveButton)
        edit_sizer.Add(self.seqName)

        sizer_toplevel = wx.FlexGridSizer(2, 6, 0, 4) # rows, cols, vgap, hgap

        # TOPLEVEL first row

        sizer_toplevel.Add(sizer_modelabels, 1, wx.EXPAND, 0)
        sizer_toplevel.Add(sizer_modecbs, 1, wx.ALL|wx.EXPAND, 0)
        sizer_toplevel.Add(sizer_matrix, 1, 0, 0)
        sizer_toplevel.Add(self.lb1, 0, wx.EXPAND, 0)
        sizer_toplevel.Add(sizer_buttons, 0, wx.ALL, 0)
        sizer_toplevel.Add(self.viewer, 0, wx.ALL, 0)

        # TOPLEVEL second row

        sizer_toplevel.Add((2,2), 0, 0, 0)
        sizer_toplevel.Add((2,2), 0, 0, 0)
        sizer_toplevel.Add(next_button)
        sizer_toplevel.Add(reload_button)
        sizer_toplevel.Add((2,2), 0, 0, 0)
        sizer_toplevel.Add(self.delButton)

        # TOPLEVEL third row

        sizer_toplevel.Add((2,2), 0, 0, 0)
        sizer_toplevel.Add((2,2), 0, 0, 0)
        sizer_toplevel.Add(cb_grid)
        sizer_toplevel.Add((2,2), 0, 0, 0)
        sizer_toplevel.Add((2,2), 0, 0, 0)
        sizer_toplevel.Add(edit_sizer)

        # OUTER sizer

        sizer_outer.Add(sizer_left)
        sizer_outer.Add(sizer_toplevel)
        sizer_outer.Add(self.crossing_label)

        self.SetSizer(sizer_outer)
        self.Layout()
        # end wxGlade

    def onSave(self, event):
        lines = self.viewer.GetItems()
        filename = 'seq/' + self.seqName.GetValue()
        with open(filename, 'w') as f:
            f.writelines(lines)
        self.report("Saved " + filename)

    def onChar(self, event):
        keycode = event.GetKeyCode()
        poofer = self.keyMap.get(keycode, None)
        if (poofer == None):
            return
        #self.report(str(keycode))
        self.trigPoofer(poofer)  # send serial command to tigger this poofer
        self.flashPooferBtn(poofer) # make this button red

    def onScroll(self, event):
        val = self.slider_gross.GetValue() + self.slider_speed.GetValue()
        self.interval = val
        self.timer.Stop()
            #self.timer.Start(val, oneShot=True)
        self.timer.Start(val)
        if val > 500:
            self.heartBeat.Start(500)
        else:
            self.heartBeat.Stop()

    def onReload(self, event):
        self.sampleList = os.listdir('seq')
        self.sampleList.remove('.svn')
        self.lb1.SetItems(self.sampleList)
        
    def onAllButton(self, event):
        self.report("ALL!")
        for i in range(16):
            self.trigPoofer(i+1)

    def onOuterButton(self, event):
        for i in [ 5, 6, 7, 8, 16, 15, 14, 13 ]:
            self.trigPoofer(i)

    def onInnerButton(self, event):
        for i in [ 1, 2, 3, 4, 12, 11, 10, 9 ]:
            self.trigPoofer(i)

    def onNextButton(self, event):
        self.seq_i = (self.seq_i+self.delta) % len(self.sequence)
        self.viewer.SetSelection(self.seq_i)
        self.doPoof()

    def onReverse(self, event):
        self.delta = -self.delta
        
    def EvtListBox(self, event):
        self.loadSequence()

    # thePoofer: 1-16
    def trigPoofer(self,thePoofer):
        self.cb_feathers[thePoofer-1].SetValue(True)
        self.timer_feathers[thePoofer-1].Start(500)

        theBoard = 1+int((thePoofer-1)/8)
        if (thePoofer > 8):
            thePoofer -= 8
        commandStr = "!0" + str(theBoard) + str(thePoofer) + "1."
        #self.report(commandStr)
        
        if self.cb_serial.GetValue():
            self.ser.write(commandStr)
            if self.ser != sys.stdout:
                self.ser.flushOutput()
            else:
                self.ser.flush()

    def goodbye(self):
        self.report("really quitting now")
        self.a.Stop()
        self.a.close()
        #self.ser.close()
        #self.Close(True)  
        #self.Destroy()

    def doLoadMenu(self):
        wildcard = "Preset files (*.pre)|*.pre|"\
            "Text (*.txt)|*.txt|" \
            "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Choose a settings file to load",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN 
            )
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.report('loading settings from "%s"' % path)
            self.setValues(self.loadSettings(path))
        dlg.Destroy()


    def doSaveMenu(self):
        dlg = wx.FileDialog(
            self, message="Save settings as ...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard="Preset files (*.pre)|*.pre", style=wx.SAVE
            )

        dlg.SetFilterIndex(2)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.report('Saving settings to "%s"' % path)
            self.saveSettings(path,self.getValues({}))
        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()


    def doResetMenu(self):
        self.report("setting default parameters")
        self.setValues(self.defaultVals())

    def doExitMenu(self):
        self.report("exiting")
        self.a.Stop()
        self.a.close()
        self.Destroy()
#
    def onCloseWindow(self, event):
        self.a.Stop()
        self.a.close()
        self.Destroy()

    def doAboutMenu(self): # wxGlade: testFrame.<event_handler>
        dlg = wx.MessageDialog(self, "ROTORBRYTE software\nby Jonathan Foote\nheadrotor@rotorbrain.com", "about", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()


    def onCheckBox(self, event): # wxGlade: testFrame.<event_handler>
        cb = event.GetEventObject()
        if cb.GetId() == AUDIO_CB:
            self.doAudioCB()
        if cb.GetId() == SERIAL_CB:
            self.report("SERIAL")
            if self.cb_serial.GetValue():
                self.report("START")
                self.timer.Start(self.interval)
            else:
                self.report("STOP")
                self.timer.Stop()
            
    def doAudioCB(self):
        if self.cb_audio.GetValue():
            self.report("Audio input started")
            self.a.Start()
        else:
            self.report("Audio input paused")
            self.a.Stop()

    def loadSequence(self):
        filename = 'seq/' + self.sampleList[self.lb1.GetSelection()]
        with open(filename, 'r') as f:
            self.sequence = f.readlines()
        self.viewer.SetItems(self.sequence)
        self.seq_i = 0
        self.viewer.SetSelection(self.seq_i)

    def doPoof(self):
        if (len(self.sequence[self.seq_i]) < 16):
            self.report ("Skipping [" + self.sequence[self.seq_i] + "]")
            return
        for i in range(16):
            #self.report(str(self.sequence[self.seq_i][i]) + " " + str(i))
            if self.sequence[self.seq_i][i] == '1':
                self.trigPoofer(i+1)
#            else:
#                if step_size > 500:
#                    self.extinguishPoofer(i+1)

        #self.report(self.sequence[self.seq_i])

    def onPoofTimeout(self, event):
        ID = event.GetId() 
        self.cb_feathers[ID-FEATHER_TIMER].SetValue(False)

    def onHeartBeat(self, event):
        self.doPoof()

    def OnTimer(self, event):
        self.doPoof()
        #print "Poof"
        if self.cb_sequence.GetValue():
            self.seq_i = (self.seq_i+self.delta) % len(self.sequence)
            self.viewer.SetSelection(self.seq_i)
            #print " Change (timer)"
            # 
            #self.timer.Start(self.lastLoudness, oneShot=True)
            
    def doMenu(self, event):
        ID = event.GetId() 
        if ID == EXIT_MENU:
            self.doExitMenu()
        elif ID == ABOUT_MENU:
            self.doAboutMenu()
        elif ID == LOAD_MENU:
            self.doLoadMenu()
        elif ID == SAVE_MENU:
            self.doSaveMenu()
        elif ID == RESET_MENU:
            self.doResetMenu()
        elif ID == AUDIO_MENU:
            pid = subprocess.Popen(["sndvol32.exe", "-Record"]).pid
        event.Skip

    def report(self,str):
        self.statusbar.SetStatusText(str)

    def saveSettings(self,fn,valDict):
        try:
            output = open(fn, 'wb')
        except IOError:
            dlg = wx.MessageDialog(self, 'Error writing settings file %s!' % fn,
                                   'Alert',
                                   wx.OK | wx.ICON_INFORMATION
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Pickle dictionary using protocol 0.
        pickle.dump(valDict, output)
        output.close()
        return

    def loadSettings(self,fn):
        try:
            input = open(fn, 'rb')
        except IOError:
            dlg = wx.MessageDialog(self, 'Error reading settings file %s!' % fn,
                                   'Alert',
                                   wx.OK | wx.ICON_INFORMATION
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            return({})
        # unpickle dictionary crap out of errors.
        try:
            valDict = pickle.load(input)
        except:
            dlg = wx.MessageDialog(self, 'Error parsing settings file %s!' % fn,
                                   'Alert',
                                   wx.OK | wx.ICON_INFORMATION
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            return({})
        input.close()
        return(valDict)

    # event responder for poofer button
    # called when poofer buttons are pressed
    def onPooferBtn(self, event): 
        button = event.GetEventObject()
        self.report("poofer button %d!" % button.chan)        
        self.trigPoofer(button.chan)  # send serial command to tigger this poofer
        self.flashPooferBtn(button.chan) # make this button red


    # turns poofer button for given channel red. 
    def flashPooferBtn(self, chan): 
        self.clearPooferBtns()
        self.pooferbtnmatrix[self.keyChannel.index(chan)].SetBackgroundColour(wx.Colour(255, 0, 0)) 

    # set all poofer buttons to default color
    def clearPooferBtns(self): 
        for button in self.pooferbtnmatrix:
            button.SetBackgroundColour(self.defaultBtnColour) 


    def onSelectColour(self, event): # wxGlade: testFrame.<event_handler>
        self.report("New color selected")
        event.Skip()

    def onAudio(self,event):
        #if self.audioActive:
        if self.cb_audio.GetValue():
            loudness = math.log(event.value)
            #self.lastLoudness = loudness
            self.gauge_audio.SetValue(int(event.value * 0.05))
            #print repr(event.value)
            if(10*loudness > self.slider_thresh.GetValue()):
                current = time.time()
                elapsed = current - self.crossing
                #if elapsed < .1:
                #    return
                
                self.crossing = current
#                self.crossing_label.SetLabel(str(int(1000*elapsed)) + " ms")

                long_elapsed = self.crossing - self.cross_list[self.cross_cursor]
                ppm = len(self.cross_list) * 60 / long_elapsed
                self.cross_list[self.cross_cursor] = self.crossing
                self.cross_cursor = (1 + self.cross_cursor) % len(self.cross_list)
                self.crossing_label.SetLabel(str(int(ppm)) + " ppm")

                self.seq_i = (self.seq_i+self.delta) % len(self.sequence)
                self.viewer.SetSelection(self.seq_i)
                self.doPoof()
                #print " Change (audio)"

            #self.graphicsPanel.drawBargraph(event.bands, height=200, width=20, pad=27)
        event.StopPropagation()   

    def InitSerial(self,comport,baudrate):
        try:
            self.ser = serial.Serial(comport, baudrate, timeout=0)  
        except serial.SerialException, v:
            dlg = wx.SingleChoiceDialog(
                self, "Can't open port "+comport+', Please select another.\n (Look in the Device Manager for available ports.\nIf no ports available, select "stdout" to test',
                "Select a port",
                ['/dev/ttyUSB0',
		 'COM1',
                 'COM2',
                 'COM3',
                 'COM4',
                 'COM5',
                 'COM6',
                 'COM7',
                 'COM8',
                 'stdout'],
                wx.CHOICEDLG_STYLE
                )
            if dlg.ShowModal() == wx.ID_OK:
                comport = dlg.GetStringSelection()
            dlg.Destroy()

            if comport == "stdout":
                self.ser = sys.stdout
                return
            try:
                self.ser = serial.Serial(comport, baudrate, timeout=1)  
            except serial.SerialException, v:
                wx.MessageBox("Serial error: could not open port %s" % comport)
                return
        
        #self.SetStatusText("Using serial port: "+ self.ser.portstr) 
        self.report("Using serial port: "+ self.ser.portstr)

    def defaultVals(self):
        initVals = {}
        # checkboxes

        initVals['audio'] = True

        initVals['setgain'] = 50
        initVals['msmooth'] = 40
        initVals['mbright'] = 75

        initVals['offs'] = 0

        for i in range(NUM_OUTCHANS):
            for j in range(NUM_CHANNELS):
                index = "spin%d_%d" % (i,j)
                initVals[index]=0
        return(initVals)


# end of class testFrame


#!/usr/bin/python
# makegamma.py
# Python program to generate gamma lookup table to
# correct LED brightness from linear PWM.
# Written by Jonathan Foote (Head Rotor at rotorbrain.com) for
# the SWARM project http://www.orbswarm.com

# calculates a function of the form out = in^gamma, rounded to nearest int

# generates an output file "gamma.h"


from math import floor


def makegamma(gamma=1.8):
    # length of table
    tablength = 256
    # maximum value in table
    tabmax = 255
    # the actual gamma exponent

    # scale factor to get output between 0 and maxn
    scale = float(tabmax)/pow(tablength,gamma)

    gammatab = []
    for i in range(tablength):
        gammatab.append(int(floor(scale*pow(i,gamma) + 0.5)))
    return(gammatab)

        
if __name__ == "__main__":

    import os
    startupfn = "startup.pre"

    LightEngine = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    topFrame = testFrame(None, -1, "")
    LightEngine.SetTopWindow(topFrame)


# XXX Default to /dev/ttyUSB0 for Linux, COM? for Windows
    topFrame.InitSerial("COM7",19200)
    topFrame.audioActive = True
    topFrame.a = AudioProc.AudioProc(topFrame,10)
    testFrame.Bind(topFrame,topFrame.a.EVT_AUDIO, topFrame.onAudio)
    topFrame.gt = makegamma(0.5)
    topFrame.Bind(wx.EVT_TIMER, topFrame.OnTimer, id=MAIN_TIMER)
    topFrame.timer = wx.Timer(topFrame, MAIN_TIMER)
    topFrame.a.Start()
    
    if os.path.exists(startupfn):
        topFrame.setValues(topFrame.loadSettings(startupfn))
    else:
        print "can't find startup settings file " + startupfn
        topFrame.setValues(topFrame.defaultVals())
        
    topFrame.Show()
    LightEngine.MainLoop()
