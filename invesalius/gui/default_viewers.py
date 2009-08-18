#--------------------------------------------------------------------------
# Software:     InVesalius - Software de Reconstrucao 3D de Imagens Medicas
# Copyright:    (C) 2001  Centro de Pesquisas Renato Archer
# Homepage:     http://www.softwarepublico.gov.br
# Contact:      invesalius@cti.gov.br
# License:      GNU - GPL 2 (LICENSE.txt/LICENCA.txt)
#--------------------------------------------------------------------------
#    Este programa e software livre; voce pode redistribui-lo e/ou
#    modifica-lo sob os termos da Licenca Publica Geral GNU, conforme
#    publicada pela Free Software Foundation; de acordo com a versao 2
#    da Licenca.
#
#    Este programa eh distribuido na expectativa de ser util, mas SEM
#    QUALQUER GARANTIA; sem mesmo a garantia implicita de
#    COMERCIALIZACAO ou de ADEQUACAO A QUALQUER PROPOSITO EM
#    PARTICULAR. Consulte a Licenca Publica Geral GNU para obter mais
#    detalhes.
#--------------------------------------------------------------------------
import sys

import wx
import wx.lib.agw.fourwaysplitter as fws
import data.viewer_slice as slice_viewer
import data.viewer_volume as volume_viewer


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=wx.Point(0, 50),
                          size=wx.Size(744, 656))

        self.__init_aui_manager()
        #self.__init_four_way_splitter()
        #self.__init_mix()

    def __init_aui_manager(self):
        self.aui_manager = wx.aui.AuiManager()
        self.aui_manager.SetManagedWindow(self)


        # TODO: Testar mais e verificar melhor opcao

        # Position
        # volume          | pos = 0
        # sagital         | pos = 1
        # coronal         | pos = 2
        # axial           | pos = 3
        # Automatico: assim que painel eh inserido ele ocupa local mais acima na janela (menor numero de posicao)

        # Layer
        # Layer 0 | Layer 1 | Layer 2 | ...
        # Automatico: todos sao colocados no mesmo layer

        # O que eh o Dockable?

        # Row
        # Row 0 | Row 1
        # Idem ao layer

        # Como funciona Direction?

        # Primeira alternativa:
        # modo: 2 no Layer 0, 2 no Layer 1 por exemplo - posicao automatica (ao inves de Layer pode ser utilizado Row)
        # problema: sash control soh aparece no sentido ertical
        # tentativa de solucionar problema seria utilizar Fixed, mas qdo se aciona maximizar nao maximiza inteiro

        p1 = slice_viewer.Viewer(self, "AXIAL")
        s1 = wx.aui.AuiPaneInfo().Centre().Row(0).\
             Name("Axial Slice").Caption("Axial slice").\
             MaximizeButton(True).CloseButton(False)

        p2 = slice_viewer.Viewer(self, "CORONAL")
        s2 = wx.aui.AuiPaneInfo().Centre().Row(0).\
             Name("Coronal Slice").Caption("Coronal slice").\
             MaximizeButton(True).CloseButton(False)

        p3 = slice_viewer.Viewer(self, "SAGITAL")
        s3 = wx.aui.AuiPaneInfo().Centre().Row(1).\
             Name("Sagital Slice").Caption("Sagital slice").\
             MaximizeButton(True).CloseButton(False)

        p4 = VolumeViewerCover(self)
        s4 = wx.aui.AuiPaneInfo().Row(1).Name("Volume").\
             Bottom().Centre().Caption("Volume").\
             MaximizeButton(True).CloseButton(False)

        if sys.platform == 'win32':
            self.aui_manager.AddPane(p1, s1)
            self.aui_manager.AddPane(p2, s2)
            self.aui_manager.AddPane(p3, s3)
            self.aui_manager.AddPane(p4, s4)
        else:
            self.aui_manager.AddPane(p4, s4)
            self.aui_manager.AddPane(p3, s3)
            self.aui_manager.AddPane(p2, s2)
            self.aui_manager.AddPane(p1, s1)

        self.aui_manager.Update()


    def __init_four_way_splitter(self):

        splitter = fws.FourWaySplitter(self, style=wx.SP_LIVE_UPDATE)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        p1 = slice_viewer.Viewer(self, "AXIAL")
        splitter.AppendWindow(p1)

        p2 = slice_viewer.Viewer(self, "CORONAL")
        splitter.AppendWindow(p2)

        p3 = slice_viewer.Viewer(self, "SAGITAL")
        splitter.AppendWindow(p3)

        p4 = volume_viewer.Viewer(self)
        splitter.AppendWindow(p4)


    def __init_mix(self):
        aui_manager = wx.aui.AuiManager()
        aui_manager.SetManagedWindow(self)


        splitter = fws.FourWaySplitter(self, style=wx.SP_LIVE_UPDATE)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)


        p1 = slice_viewer.Viewer(self, "AXIAL")
        aui_manager.AddPane(p1,
                                 wx.aui.AuiPaneInfo().
                                 Name("Axial Slice").Caption("Axial slice").
                                 MaximizeButton(True).CloseButton(False))

        p2 = slice_viewer.Viewer(self, "CORONAL")
        aui_manager.AddPane(p2,
                                 wx.aui.AuiPaneInfo().
                                 Name("Coronal Slice").Caption("Coronal slice").
                                 MaximizeButton(True).CloseButton(False))

        p3 = slice_viewer.Viewer(self, "SAGITAL")
        aui_manager.AddPane(p3,
                                 wx.aui.AuiPaneInfo().
                                 Name("Sagittal Slice").Caption("Sagittal slice").
                                 MaximizeButton(True).CloseButton(False))

        #p4 = volume_viewer.Viewer(self)
        aui_manager.AddPane(VolumeViewerCover,
                                 wx.aui.AuiPaneInfo().
                                 Name("Volume").Caption("Volume").
                                 MaximizeButton(True).CloseButton(False))

        splitter.AppendWindow(p1)
        splitter.AppendWindow(p2)
        splitter.AppendWindow(p3)
        splitter.AppendWindow(p4)


        aui_manager.Update()







import wx.lib.platebtn as pbtn
import wx.lib.buttons as btn
import wx.lib.pubsub as ps
import wx.lib.colourselect as csel
import constants as const

[BUTTON_RAYCASTING, BUTTON_VIEW] = [wx.NewId() for num in xrange(2)]
RAYCASTING_TOOLS = wx.NewId()

ID_TO_BMP = {const.VOL_FRONT: ["Front", "../icons/view_front.png"],
             const.VOL_BACK: ["Back", "../icons/view_back.png"],
             const.VOL_TOP: ["Top", "../icons/view_top.png"],
             const.VOL_BOTTOM: ["Bottom", "../icons/view_bottom.png"],
             const.VOL_RIGHT: ["Right", "../icons/view_right.png"], 
             const.VOL_LEFT: ["Left", "../icons/view_left.png"],
             const.VOL_ISO:["Isometric","../icons/view_isometric.png"]
             }

ID_TO_NAME = {}
ID_TO_TOOL = {}
ID_TO_TOOL_ITEM = {}

class VolumeViewerCover(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(volume_viewer.Viewer(self), 1, wx.EXPAND|wx.GROW)
        sizer.Add(VolumeToolPanel(self), 0, wx.EXPAND)
        self.SetSizer(sizer)
        sizer.Fit(self)

class VolumeToolPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size = (8,100))

        # VOLUME RAYCASTING BUTTON
        BMP_RAYCASTING = wx.Bitmap("../icons/volume_raycasting.png",
                                    wx.BITMAP_TYPE_PNG)

        # MENU RELATED TO RAYCASTING TYPES
        menu = wx.Menu()
        for name in const.RAYCASTING_TYPES:
            id = wx.NewId()
            item = wx.MenuItem(menu, id, name, kind=wx.ITEM_RADIO)
            menu.AppendItem(item)
            if name == const.RAYCASTING_OFF_LABEL:
                item.Check(1)
            ID_TO_NAME[id] = name

        menu.AppendSeparator()
        # MENU RELATED TO RAYCASTING TOOLS
        submenu = wx.Menu()
        for name in const.RAYCASTING_TOOLS:
           id = wx.NewId()
           item = wx.MenuItem(submenu, id, name, kind=wx.ITEM_CHECK)
           submenu.AppendItem(item)
           ID_TO_TOOL[id] = name
           ID_TO_TOOL_ITEM[id] = item
        #submenu.Enable(0)   
        self.submenu_raycasting_tools = submenu
        menu.AppendMenu(RAYCASTING_TOOLS, "Tools", submenu)
        menu.Enable(RAYCASTING_TOOLS, 0)

        self.menu_raycasting = menu
        menu.Bind(wx.EVT_MENU, self.OnMenuRaycasting)    

        button_raycasting = pbtn.PlateButton(self, BUTTON_RAYCASTING,"",
                BMP_RAYCASTING, style=pbtn.PB_STYLE_SQUARE,
                size=(24,24))
        button_raycasting.SetMenu(menu)
        
        self.button_raycasting = button_raycasting

        # VOLUME VIEW ANGLE BUTTON
        menu = wx.Menu()
        for id in ID_TO_BMP:
            bmp =  wx.Bitmap(ID_TO_BMP[id][1], wx.BITMAP_TYPE_PNG)
            item = wx.MenuItem(menu, id, ID_TO_BMP[id][0])
            item.SetBitmap(bmp)
            menu.AppendItem(item)
        menu.Bind(wx.EVT_MENU, self.OnMenuView)
        self.menu_view = menu

        BMP_FRONT = wx.Bitmap(ID_TO_BMP[const.VOL_FRONT][1],
                              wx.BITMAP_TYPE_PNG)
        button_view = pbtn.PlateButton(self, BUTTON_VIEW, "",
                                        BMP_FRONT, size=(24,24),
                                        style=pbtn.PB_STYLE_SQUARE)
        button_view.SetMenu(menu)
        self.button_view = button_view

        # VOLUME COLOUR BUTTOM
        button_colour= csel.ColourSelect(self, 111,colour=(0,0,0),
                                        size=(24,24))
        button_colour.Bind(csel.EVT_COLOURSELECT, self.OnSelectColour)
        self.button_colour = button_colour

        self.__bind_events()
        # SIZER TO ORGANIZE ALL
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(button_colour, 0, wx.ALL, 1)
        sizer.Add(button_raycasting, 0, wx.ALL, 1)
        sizer.Add(button_view, 0, wx.ALL, 1)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def __bind_events(self):
        ps.Publisher().subscribe(self.ChangeButtonColour,
                                 'Change volume viewer gui colour')

    def ChangeButtonColour(self, pubsub_evt):
        colour = [i*255 for i in pubsub_evt.data]
        self.button_colour.SetColour(colour)

    def OnMenuRaycasting(self, evt):
        """Events from raycasting menu."""
        id = evt.GetId()
        if id in ID_TO_NAME.keys():
            # Raycassting type was selected
            name = ID_TO_NAME[evt.GetId()]
            ps.Publisher().sendMessage('Load raycasting preset',
                                          ID_TO_NAME[evt.GetId()])
            # Enable or disable tools
            if name != const.RAYCASTING_OFF_LABEL:
 	            self.menu_raycasting.Enable(RAYCASTING_TOOLS, 1)
            else:
                self.menu_raycasting.Enable(RAYCASTING_TOOLS, 0)
            
        else:
            # Raycasting tool 
            # TODO: In future, when more tools are available
            item = ID_TO_TOOL_ITEM[evt.GetId()]
            #if not item.IsChecked():
            #    for i in ID_TO_TOOL_ITEM.values():
            #        if i is not item:
            #            i.Check(0)
            if item.IsChecked():
                ps.Publisher().sendMessage('Enable raycasting tool',
                                          [ID_TO_TOOL[evt.GetId()],1])
            else:
                ps.Publisher().sendMessage('Enable raycasting tool',
                                            [ID_TO_TOOL[evt.GetId()],0])
                        

    def OnMenuView(self, evt):
        """Events from button menus."""
        bmp = wx.Bitmap(ID_TO_BMP[evt.GetId()][1], wx.BITMAP_TYPE_PNG)
        self.button_view.SetBitmapSelected(bmp)
        
        ps.Publisher().sendMessage('Set volume view angle',
                                   evt.GetId())

    def OnSelectColour(self, evt):
        colour = c = [i/255.0 for i in evt.GetValue()]
        ps.Publisher().sendMessage('Change volume viewer background colour', colour)

