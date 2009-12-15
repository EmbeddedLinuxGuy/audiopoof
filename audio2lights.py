#!C:/Python25/Python.exe
#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# generated by wxGlade 0.6.3 on Wed Feb 18 17:53:41 2009

import wx
import sys
import os
import wx.lib.colourselect as CSel
import serial
import pickle
import subprocess

#for rgb2hsv
import colorsys

# local goodness
import TestPanel
import AudioProc


# 
SLIDER_HUE = 91
SLIDER_OFFS = 92
SLIDER_SETGAIN = 93
SLIDER_MSMOOTH = 94
SLIDER_MBRIGHT = 95

CSEL_INDEX = 80

PRESET_INDEX = 200

EXIT_MENU = 50
ABOUT_MENU = 51
LOAD_MENU = 52
SAVE_MENU = 53
FILE_MENU = 54
RESET_MENU = 55
AUDIO_MENU = 56

MATRIX_CB = 70
AUDIO_CB = 71
OUTPUT_CB = 72

# global constants

NUM_PRESETS = 7
NUM_CHANNELS = 8                  # number of spectrographic channels
NUM_OUTCHANS = 3                  # number of output channels




class testFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: testFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.sizer_presets_staticbox = wx.StaticBox(self, -1, "presets")
        
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
        self.label_hue = wx.StaticText(self, -1, "Hue\ncenter", style=wx.ALIGN_CENTRE)
        self.label_offs = wx.StaticText(self, -1, "Hue\noffset", style=wx.ALIGN_CENTRE)
        self.label_setgain = wx.StaticText(self, -1, "Audio\ngain", style=wx.ALIGN_CENTRE)
        self.label_msmooth = wx.StaticText(self, -1, "master\nsmooth")
        self.label_mbright = wx.StaticText(self, -1, "master\nbright")
        self.slider_hue = wx.Slider(self, SLIDER_HUE, 0, 0, 99, style=wx.SL_VERTICAL|wx.SL_LABELS|wx.SL_INVERSE)
        self.slider_offs = wx.Slider(self, SLIDER_OFFS, 0, 0, 99, style=wx.SL_VERTICAL|wx.SL_LABELS|wx.SL_INVERSE)
        self.slider_setgain = wx.Slider(self, SLIDER_SETGAIN, 50, 0, 99, style=wx.SL_VERTICAL|wx.SL_LABELS|wx.SL_INVERSE)
        self.graphicsPanel = TestPanel.TestPanel(self, -1)
        self.slider_msmooth = wx.Slider(self, SLIDER_MSMOOTH, 50, 0, 99, style=wx.SL_VERTICAL|wx.SL_LABELS|wx.SL_INVERSE)
        self.slider_mbright = wx.Slider(self, SLIDER_MBRIGHT, 50, 0, 99, style=wx.SL_VERTICAL|wx.SL_LABELS|wx.SL_INVERSE)
        self.label_mode = wx.StaticText(self, -1, "mode", style=wx.ALIGN_CENTRE)
        self.label_outputCB = wx.StaticText(self, -1, "Output")
        self.label_matrixcb = wx.StaticText(self, -1, "Matrix")
        self.label_audio_cb = wx.StaticText(self, -1, "Audio")
        self.cb_output = wx.CheckBox(self, OUTPUT_CB, "")
        self.cb_matrix = wx.CheckBox(self, MATRIX_CB, "")
        self.cb_audio = wx.CheckBox(self, AUDIO_CB, "")

        self.gauge_audio = wx.Gauge(self, -1, 100, style=wx.GA_VERTICAL|wx.GA_SMOOTH)
        self.indicator = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)

        self.orb_cbs = []
        for i in range(6):               # create orb enable checkboxen
            cb = wx.CheckBox(self, OUTPUT_CB, "orb 6%d" %i)
            cb.orbn = 60 + i
            self.orb_cbs.append(cb)


        # this loop creates the SpinCntl matrix
        self.spinmatrix = []    # array of spincontrol rows
        self.csel= []           # array of spincontrols, one per column
        self.chancb = []        # array of output channel check boxes, one per row
        for i in range(NUM_OUTCHANS): # creates one row per outchan
            self.spinmatrix.append([])
            for j in range(NUM_CHANNELS): # creates one spinctrl per spectrograph channel
                sc = wx.SpinCtrl(self, -1, "0", min=-9, max=9, style=wx.SP_ARROW_KEYS|wx.TE_AUTO_URL|wx.TE_RIGHT)
                sc.chan = j
                sc.outc = i
                sc.SetMinSize((40, -1))
                #sc.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 1, ""))
                #sc.SetBackgroundColour(wx.Colour(148, 255, 153)) Doh! Bug!
                self.spinmatrix[i].append(sc)
            csel_label = "chan %s" % i
            
            cs = CSel.ColourSelect(self, i + CSEL_INDEX, label=csel_label, colour=(0,0,0))
            self.Bind(CSel.EVT_COLOURSELECT, self.onSelectColour, cs)
            self.csel.append(cs)
            cb = wx.CheckBox(self, -1, "ON")
            cb.SetMinSize((40, -1))
            cb.outc = i
            cb.name = "chancb%d" % i
            self.chancb.append(cb)

        self.label_audioin = wx.StaticText(self, -1, "Audio\n  In")


        # this loop creates the row of preset buttons
        self.preset_buttons = []
        for i in range(NUM_PRESETS):
            self.preset_buttons.append(wx.Button(self, PRESET_INDEX + i, "preset %d" % i))
            self.preset_buttons[i].SetMinSize((50, -1))
            self.preset_buttons[i].presetN = i
            self.Bind(wx.EVT_BUTTON, self.doPresetBtn, self.preset_buttons[i])
        self.store_preset = wx.Button(self, PRESET_INDEX + NUM_PRESETS, "STORE")
        self.Bind(wx.EVT_BUTTON, self.doStorePresetBtn, self.store_preset)
        self.store_preset.presetN = NUM_PRESETS

        self.__set_properties()
        self.__do_layout()


 
        self.Bind(wx.EVT_MENU, self.doMenu)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.onScroll, id=SLIDER_HUE)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.onScroll, id=SLIDER_OFFS)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.onScroll, id=SLIDER_SETGAIN)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.onScroll, id=SLIDER_MSMOOTH)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.onScroll, id=SLIDER_MBRIGHT)
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

        self.Bind(wx.EVT_CHECKBOX, self.onCheckBox, id=AUDIO_CB)
        self.Bind(wx.EVT_CHECKBOX, self.onCheckBox, id=MATRIX_CB)

        # end wxGlade

    def __set_properties(self):

        self.storeFlag = 0

        # begin wxGlade: testFrame.__set_properties
        self.SetTitle("r o t o r b r y t e")
        self.SetSize((800, 465))
        self.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.statusbar.SetStatusWidths([-1])

        self.label_hue.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_offs.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_setgain.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_msmooth.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_mbright.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.slider_hue.SetMinSize((-1, -1))
        self.slider_hue.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.slider_offs.SetMinSize((-1, -1))
        self.slider_offs.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.slider_setgain.SetMinSize((-1, -1))
        self.slider_setgain.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.graphicsPanel.SetMinSize((450,200))
        self.graphicsPanel.SetBackgroundColour(wx.Colour(221, 221, 221))
        self.slider_msmooth.SetMinSize((-1, -1))
        self.slider_msmooth.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.slider_msmooth.oldval = "-1" # check this val to see if slider has changed
        self.slider_mbright.SetMinSize((-1, -1))
        self.slider_mbright.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.label_mode.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.indicator.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.store_preset.SetMinSize((50, -1))
        self.store_preset.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def setValues(self,valDict):
        if len(valDict) < 2:
            return

        for cb in self.chancb:
            cb.SetValue(valDict[cb.name])
            
        self.cb_output.SetValue(valDict['output'])
        self.cb_matrix.SetValue(valDict['matrix'])
        self.slider_setgain.SetValue(valDict['setgain'])
        self.doSetgain()
        self.slider_mbright.SetValue(valDict['mbright'])
        self.slider_msmooth.SetValue(valDict['msmooth'])
        self.slider_hue.SetValue(valDict['hue'])
        self.slider_offs.SetValue(valDict['offs'])
        for i in range(NUM_OUTCHANS):
            self.csel[i].SetColour(valDict["csel%d"%i])
            for j in range(NUM_CHANNELS):
                index = "spin%d_%d" % (i,j)
                self.spinmatrix[i][j].SetValue(valDict[index])
        self.report("Parameters updated")        


    def getValues(self,valDict):

        for cb in self.chancb:
            valDict[cb.name] = cb.GetValue()

        valDict['output'] = self.cb_output.GetValue()
        valDict['matrix'] = self.cb_matrix.GetValue()

        valDict['setgain'] = self.slider_setgain.GetValue()
        valDict['mbright'] = self.slider_mbright.GetValue()
        valDict['msmooth'] = self.slider_msmooth.GetValue()

        valDict['hue'] = self.slider_hue.GetValue()
        valDict['offs'] = self.slider_offs.GetValue()

        for i in range(NUM_OUTCHANS):
            valDict["csel%d"%i] = self.csel[i].GetColour()
            for j in range(NUM_CHANNELS):
                index = "spin%d_%d" % (i,j)
                valDict[index] = self.spinmatrix[i][j].GetValue()


        return(valDict)

    def __do_layout(self):
        # begin wxGlade: testFrame.__do_layout
        sizer_toplevel = wx.FlexGridSizer(4, 8, 0, 4)
        sizer_presets = wx.StaticBoxSizer(self.sizer_presets_staticbox, wx.HORIZONTAL)
        sizer_matrix = wx.GridSizer(NUM_OUTCHANS, NUM_CHANNELS+2, 5, 1)
        sizer_modecbs = wx.GridSizer(5, 1, 0, 0)
        sizer_orbcbs = wx.GridSizer(6, 1, 0, 0)
        sizer_modelabels = wx.GridSizer(5, 1, 0, 0)
        sizer_indicator = wx.BoxSizer(wx.VERTICAL)

        # TOPLEVEL first row
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add(self.label_offs, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, 0)
        sizer_toplevel.Add(self.label_hue, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, 0)
        sizer_toplevel.Add(self.label_setgain, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add(self.label_msmooth, 0, wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, 4)
        sizer_toplevel.Add(self.label_mbright, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, 3)

        # TOPLEVEL second row
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        for i in range(6):
            sizer_orbcbs.Add(self.orb_cbs[i])
        sizer_toplevel.Add(sizer_orbcbs, 1, wx.EXPAND, 0)
#        sizer_toplevel.Add((20, 20), 0, 0, 0) # spacer instead of offs slider
        sizer_toplevel.Add(self.slider_offs, 0, wx.EXPAND, 0)
        sizer_toplevel.Add(self.slider_hue, 0, wx.EXPAND, 0)
        sizer_toplevel.Add(self.slider_setgain, 0, wx.EXPAND, 0)
        sizer_toplevel.Add(self.graphicsPanel, 0, 0, 0)
        sizer_toplevel.Add(self.slider_msmooth, 0, wx.EXPAND, 0)
        sizer_toplevel.Add(self.slider_mbright, 0, wx.EXPAND, 0)

        # TOPLEVEL third row
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_modelabels.Add((20, 20), 0, 0, 0)
        sizer_modelabels.Add(self.label_mode, 0, wx.ALIGN_RIGHT, 0)
        sizer_modelabels.Add(self.label_outputCB, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modelabels.Add(self.label_matrixcb, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modelabels.Add(self.label_audio_cb, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_toplevel.Add(sizer_modelabels, 1, wx.EXPAND, 0)
        sizer_modecbs.Add((20, 20), 0, 0, 0)
        sizer_modecbs.Add((20, 20), 0, 0, 0)
        sizer_modecbs.Add(self.cb_output, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modecbs.Add(self.cb_matrix, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_modecbs.Add(self.cb_audio, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_toplevel.Add(sizer_modecbs, 1, wx.ALL|wx.EXPAND, 0)
        sizer_toplevel.Add(self.gauge_audio, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # for each row in the output array
        for i in range(NUM_OUTCHANS):
            # first add NUM_OUTCHANS spin controls
            for j in range(NUM_CHANNELS):
                sizer_matrix.Add(self.spinmatrix[i][j])
            # then at the end of the row add the csel and the checkbox
            sizer_matrix.Add(self.csel[i],0, wx.ALIGN_CENTER_VERTICAL, 0)
            sizer_matrix.Add(self.chancb[i],0, wx.ALIGN_CENTER_VERTICAL, 0)

        sizer_toplevel.Add(sizer_matrix, 1, 0, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_indicator.Add((21, 20), 0, 0, 0)
        sizer_indicator.Add(self.indicator, 1, wx.EXPAND, 0)
        sizer_indicator.Add((21, 20), 0, 0, 0)
        sizer_toplevel.Add(sizer_indicator, 1, wx.EXPAND, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add(self.label_audioin, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        for i in range(7):
            sizer_presets.Add(self.preset_buttons[i], 0, wx.ALL|wx.EXPAND, 3)

        sizer_presets.Add(self.store_preset, 0, wx.EXPAND, 0)
        sizer_toplevel.Add(sizer_presets, 1, wx.EXPAND, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        sizer_toplevel.Add((20, 20), 0, 0, 0)
        self.SetSizer(sizer_toplevel)
        self.Layout()
        # end wxGlade

    def setIndicator(self,theC):
        #map colors through gamma table
        theColor = wx.Colour(self.gt[theC[0]],
                             self.gt[theC[1]],
                             self.gt[theC[2]])
#        theColor = wx.Colour(theC[0],
#                             theC[1],
#                             theC[2])
        self.indicator.SetBackgroundColour(theColor)
        self.indicator.Refresh()

    def setOrbOutput(self,theColor):
        noOrbSelected = True
        for n, cb in enumerate(self.orb_cbs):

            if cb.GetValue():
                noOrbSelected = False
                # convert to hue and add offset for each orb
                theHSV = colorsys.rgb_to_hsv(theColor[0],theColor[1],theColor[2])
                newhue = theHSV[0] + n*self.slider_offs.GetValue()/200.0
                while(newhue > 1.0):
                    newhue -= 1.0
                outColor = list(colorsys.hsv_to_rgb(newhue,theHSV[1],theHSV[2]))

                # orb-sepcific preamble
                theOrb= "%d " % (n + 60)
                self.setOutput(theOrb,outColor)
                self.ser.write("}")
        if (noOrbSelected):              # else... no orb checkboxes set
            self.setOutput("60",theColor)


    def setOutput(self,theOrb,theColor):
        """output array of 0-1 floats as color, converting to byte range"""

       # convert to hue and add offset
        theHSV = colorsys.rgb_to_hsv(theColor[0],theColor[1],theColor[2])
        newhue = theHSV[0] + self.slider_hue.GetValue()/100.0
        while(newhue > 1.0):
            newhue -= 1.0
        theColor = list(colorsys.hsv_to_rgb(newhue,theHSV[1],theHSV[2]))
        

        for i in range(len(theColor)):
            theColor[i] = int(theColor[i] * self.slider_mbright.GetValue()/100)
            if theColor[i] > 255:
                theColor[i] = 255
            if theColor[i] < 0:
                theColor[i] = 0
        self.setIndicator(theColor)        
        if self.cb_output.GetValue():
            RGBstr = self.getRGBStr(theOrb,theColor)
            #self.report(RGBstr)
            self.ser.write(RGBstr)
            smoothval = str(self.slider_msmooth.GetValue())
            if (smoothval != self.slider_msmooth.oldval):
                self.slider_msmooth.oldval = smoothval
                self.ser.write("{%s <LT%s>}" % (theOrb,smoothval))
                self.report("Smooth val set to " + smoothval)

            self.ser.flushInput()
            self.ser.flushOutput()


    

    def getHueStr(self,hue):
        fbright = 1.0
        colors = colorsys.hsv_to_rgb(hue, 1.0, fbright)
        outstr =   "<LR%d>" % int(colors[0]*255)
        outstr +=  "<LG%d>" % int(colors[1]*255)
        outstr +=  "<LB%d>" % int(colors[2]*255)
        outstr +=  "<LF>"
        return(outstr)

    def getRGBStr(self,theOrb,theColor):
        outstr =   "{%s <LR%d>}" % (theOrb,int(theColor[0]))
        outstr +=  "{%s <LG%d>}" % (theOrb,int(theColor[1]))
        outstr +=  "{%s <LB%d>}" % (theOrb,int(theColor[2]))
        outstr +=  "{%s <LF>}" % theOrb
        return(outstr)

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
            
    def doAudioCB(self):
        if self.cb_audio.GetValue():
            self.report("Audio input started")
            self.a.Start()
        else:
            self.report("Audio input paused")
            self.a.Stop()

    def onScroll(self, event): # wxGlade: testFrame.<event_handler>
        slider = event.GetEventObject()
        val = slider.GetValue()
	if slider.GetId() == SLIDER_SETGAIN:
           self.report("Audio gain set to " + str(val)) 
           self.a.setgain(val)
        elif slider.GetId() == SLIDER_MSMOOTH:
            self.report("Fade time set to " + str(val))
        elif slider.GetId() == SLIDER_MBRIGHT:
            self.report("Gain set to " + str(val)) 
#        event.Skip()

    def doSetgain(self):
        gain = self.slider_setgain.GetValue()
        self.a.setgain(gain)
        self.report("Audio input gain set to %d" % gain)


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
        print str
        sys.stdout.flush()
        self.statusbar.SetStatusText(str)

        # print to status bar and/or stderr

    def getPresetFileName(self,n):
        presetfn = "preset%1d.pre" % n
        return(presetfn)

    def savePreset(self,n,valDict):
        self.saveSettings(self.getPresetFileName(n),valDict)

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

    def loadPreset(self,n):
        fn = self.getPresetFileName(n)
        try:
            input = open(fn, 'rb')
        except IOError:
            dlg = wx.MessageDialog(self, 'No data stored for preset %d!' % n,
                                   'Alert',
                                   wx.OK | wx.ICON_INFORMATION
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            return({})
        input.close()
        return(self.loadSettings(fn))
        
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

    def doPresetBtn(self, event): # wxGlade: testFrame.<event_handler>
        button = event.GetEventObject()
        if self.storeFlag:
            self.report("storing preset %d" % button.presetN)        
            valDict = self.getValues({})
            self.savePreset(button.presetN,valDict)
        else:                   # load preset
            self.report("loading preset %d" % button.presetN)
            self.setValues(self.loadPreset(button.presetN))
        self.storeFlag = 0
        self.doColorStorePresetBtn(self.storeFlag)
        #event.Skip()

    def doStorePresetBtn(self, event): 
        self.storeFlag = 1-self.storeFlag # toggle self.storeFlag between 1 and 0
        if self.storeFlag:
            self.report("select preset to store")
        else:
            self.report("store preset cancelled")
        self.doColorStorePresetBtn(self.storeFlag)
        #event.Skip()

    # change the color on the store button to indicate storage mode
    def doColorStorePresetBtn(self,state):
        if(state):
            self.store_preset.SetBackgroundColour(wx.Colour(148, 255, 153)) 
        else:
            self.store_preset.SetBackgroundColour(wx.Colour(236, 233, 216))

    def onSelectColour(self, event): # wxGlade: testFrame.<event_handler>
        self.report("New color selected")
        event.Skip()

    def onAudio(self,event):
        #if self.audioActive:
        if self.cb_audio.GetValue():
            self.gauge_audio.SetValue(int(event.value * 0.5))
            self.graphicsPanel.drawBargraph(event.bands, height=200, width=20, pad=27)
            outval = [0,0,0]
            for oc in range(NUM_OUTCHANS):
                if self.chancb[oc].GetValue():
                    channelout = 0
                    numbands = 0
                    # get channel color from row ColourSelect
                    cc = self.csel[oc].GetColour()
                    # get as tuple
                    ccolor = cc.Get()
                    # sum power across spectral bands for this output.
                    for i in range(len(event.bands)):

                        channelout += event.bands[i] * self.spinmatrix[oc][i].GetValue()
                        if event.bands[i] != 0:
                            numbands += 1
                    if numbands > 0:        # average by number of non-zero bands
                        channelout /= numbands

                    # add the contribution of this channel to this rgb color
                    for c in range(3):
                        outval[c] += channelout * ccolor[c] 
            if self.cb_matrix.GetValue():
                self.setOrbOutput(outval)
        event.StopPropagation()   
#        event.Skip()

    def InitSerial(self,comport,baudrate):
        try:
            self.ser = serial.Serial(comport, baudrate, timeout=0)  
        except serial.SerialException, v:
            dlg = wx.SingleChoiceDialog(
                self, "Can't open port "+comport+', Please select another.\n (Look in the Device Manager for available ports.\nIf no ports available, select "stdout" to test',
                "Select a port",
                ['COM1',
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

        for cb in self.chancb:
            initVals[cb.name] = True
            
        initVals['output'] = True
        initVals['audio'] = True
        initVals['matrix'] = True

        initVals['setgain'] = 50
        initVals['msmooth'] = 40
        initVals['mbright'] = 75

        initVals['hue'] = 0
        initVals['offs'] = 0

        initVals['csel0'] = (255,0,0)
        initVals['csel1'] = (0,255,0)
        initVals['csel2'] = (0,0,255)
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


#    topFrame.InitSerial("COM6",115200)
    topFrame.InitSerial("COM6",38400)
    topFrame.audioActive = True
    topFrame.a = AudioProc.AudioProc(topFrame,10)
    testFrame.Bind(topFrame,topFrame.a.EVT_AUDIO, topFrame.onAudio)
    topFrame.gt = makegamma(0.5)
    topFrame.a.Start()
    
    if os.path.exists(startupfn):
        topFrame.setValues(topFrame.loadSettings(startupfn))
    else:
        print "can't find startup settings file " + startupfn
        topFrame.setValues(topFrame.defaultVals())
        
    topFrame.Show()
    LightEngine.MainLoop()
