"""VelocityOne V1 Mapper. Run normally for hardware; --render produces a real Qt render for QA."""
import ctypes,json,os,pathlib,re,subprocess,sys,time
from PySide6.QtCore import Qt,QTimer,QUrl
from PySide6.QtGui import QFont,QDesktopServices,QAction,QFontDatabase,QIcon,QPixmap
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,
    QLabel,QPushButton,QComboBox,QLineEdit,QSplitter,QTabWidget,QScrollArea,QFrame,
    QTableWidget,QTableWidgetItem,QHeaderView,QGridLayout,QFormLayout,QDoubleSpinBox,QDialog,QDialogButtonBox,QSpinBox,QMessageBox,QFileDialog,QInputDialog,QSizePolicy)
from core import default_profile,validate_profile,evaluate,source_value,AXES,BUTTONS
from input_device import Flightstick
from engine import Engine
from widgets import ControllerView,AxisMeter,ButtonMonitor,SourceDialog,source_text,REGIONS,THUMBWHEEL_SETUP,OutputInputsDialog
from calibration import apply_calibration,clear_unverified_levers
from calibration_dialog import CalibrationDialog
from macro_dialog import MacroDialog
from overlay_bindings import apply_reported_layout
from game_presets import GAMES,CUSTOM_GAME,starter_ids,starter_name,make_starter,upgrade_legacy_action_labels
from profile_library import list_presets,save_preset
from runtime_paths import select_data_root,prepare_user_data,stage_driver_installer

SOURCE_DIR=pathlib.Path(__file__).parent
FROZEN=getattr(sys,'frozen',False)
APP_DIR=pathlib.Path(sys.executable).parent if FROZEN else SOURCE_DIR
RESOURCE_ROOT=pathlib.Path(getattr(sys,'_MEIPASS',SOURCE_DIR))
_data_index=sys.argv.index('--data-dir')+1 if '--data-dir' in sys.argv else None
_data_override=sys.argv[_data_index] if _data_index is not None and _data_index<len(sys.argv) else None
ROOT=select_data_root(FROZEN,SOURCE_DIR,os.environ.get('LOCALAPPDATA',str(pathlib.Path.home()/'AppData'/'Local')),_data_override)
ASSETS=RESOURCE_ROOT/'assets'
KEYS={**{chr(i):i for i in range(65,91)},**{str(i):48+i for i in range(10)},
      **{f'F{i}':111+i for i in range(1,25)},'Space':32,'Enter':13,'Escape':27,'Tab':9,
      'Backspace':8,'Shift':16,'Control':17,'Alt':18,'Up':38,'Down':40,'Left':37,'Right':39,
      'Insert':45,'Delete':46,'Home':36,'End':35,'Page Up':33,'Page Down':34}

from ui_theme import STYLE
from xbox_symbols import XboxSymbol
from window_theme import DarkWindowFrames
from axis_assignment import AxisAssignmentButton

def label(text,kind=None):
    w=QLabel(text)
    if kind:w.setObjectName(kind)
    return w

def button(text,callback,kind=None):
    b=QPushButton(text);b.clicked.connect(callback)
    if kind:b.setObjectName(kind)
    return b

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VelocityOne V1 • Flightstick Mapper')
        self.setWindowIcon(QIcon(str(ASSETS/'controlstation.ico')))
        QApplication.instance().setWindowIcon(self.windowIcon())
        screen=QApplication.primaryScreen().availableGeometry()
        self.setMinimumSize(1100,650)
        self.resize(min(1640,screen.width()),min(1000,screen.height()))
        self.closing=False
        self.p=apply_reported_layout(default_profile())
        self.state=None
        self.device=Flightstick()
        self.engine=Engine(ROOT,RESOURCE_ROOT)
        self.selected_region='roll'
        self.rows={}
        self.target_labels={}
        self.target_symbols={}
        self.current_path=None
        self._baseline=None
        prepare_user_data(ROOT,[APP_DIR,APP_DIR/'VelocityOneMapper'] if FROZEN else [])

        main=QWidget()
        self.setCentralWidget(main)
        content=QVBoxLayout(main)
        content.setContentsMargins(10,6,10,6)
        content.setSpacing(6)
        header=QHBoxLayout()
        titles=QVBoxLayout()
        titles.setSpacing(2)
        titles.addWidget(label('VELOCITYONE  /  ORIGINAL V1','eyebrow'))
        titles.addWidget(label('Flightstick workspace','title'))
        header.addLayout(titles)
        header.addStretch()
        header.addWidget(label('Emergency stop  Ctrl + Alt + F12','muted'))
        self.connected=label('CONNECTING…','badge')
        self.macro_button=QAction('Macros…',self)
        self.macro_button.triggered.connect(self.edit_macros)
        header.addWidget(self.connected)
        # Application identity is in the window title; keep space for assignments.
        self.connected.setToolTip('Original VelocityOne V1 connection status')

        toolbar=QHBoxLayout()
        brand=QLabel();brand.setFixedWidth(38)
        brand.setPixmap(QPixmap(str(ASSETS/'controlstation.png')).scaled(34,34,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        brand.setToolTip('VelocityOne V1 ControlStation')
        toolbar.addWidget(brand)
        profile_box,pf=self.panel('navGroup')
        pf.addWidget(label('01  GAME → USER PRESET','eyebrow'))
        game_row=QHBoxLayout()
        game_row.addWidget(label('Game','muted'))
        self.game_selector=QComboBox()
        self.game_selector.setEditable(True)
        self.game_selector.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.game_selector.setToolTip('Select a game, or type a custom game name and press Enter.')
        game_row.addWidget(self.game_selector,1)
        profile_row=game_row
        profile_row.addWidget(label('Preset','muted'))
        self.profiles=QComboBox()
        self.profiles.setMinimumWidth(150)
        profile_row.addWidget(self.profiles,2)
        self.name=QLineEdit(self.p['name'])
        self.name.setPlaceholderText('Name your user preset')
        self.name.setMinimumWidth(100)
        self.name.hide()
        pf.addLayout(profile_row)
        self.reload_profiles()
        self.profiles.activated.connect(self.load_selected)
        self.game_selector.activated.connect(self.game_changed)
        self.game_selector.lineEdit().editingFinished.connect(self.custom_game_finished)
        toolbar.addWidget(profile_box,3)
        output_box,ob=self.panel('navGroup')
        ob.addWidget(label('02  GAME OUTPUT','eyebrow'))
        output_row=QHBoxLayout()
        self.mode=QComboBox()
        self.mode.addItems(['Xbox gamepad','Keyboard / mouse'])
        self.mode.currentTextChanged.connect(lambda _:self.stop())
        self.mode.currentTextChanged.connect(self.update_symbol_visibility)
        output_row.addWidget(self.mode,1)
        output_row.addWidget(self.connected)
        self.start_button=button('Start output',self.start_output,'primary')
        output_row.addWidget(self.start_button)
        output_row.addWidget(button('Stop',self.stop,'stop'))
        ob.addLayout(output_row)
        toolbar.addWidget(output_box,2)
        content.addLayout(toolbar)
        self.notice=label('SETUP  •  Identify V1 controls first, then select any assignment to learn its physical input.','notice')
        self.notice.setWordWrap(True)
        content.addWidget(self.notice)

        split=QSplitter(Qt.Orientation.Horizontal)
        split.setHandleWidth(8)
        split.setChildrenCollapsible(False)
        content.addWidget(split,1)
        left,left_layout=self.scroll_page()
        left.setMinimumWidth(660)
        controls_grid=QGridLayout();controls_grid.setContentsMargins(0,0,0,0)
        controls_grid.setHorizontalSpacing(10);controls_grid.setVerticalSpacing(10)
        controls_grid.setColumnStretch(0,1);controls_grid.setColumnStretch(1,1)
        controls_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.addLayout(controls_grid)
        left_layout.addStretch()
        axes,al=self.panel('axisGroup',8)
        al.setAlignment(Qt.AlignmentFlag.AlignTop)
        al.addWidget(label('03  FLIGHT & CAMERA','axisHeading'))
        self.mapping_rows(al,('LX','LY','RX','RY'))
        dz=QHBoxLayout()
        dz.addWidget(label('Stick dead zone','muted'))
        self.deadzone=QDoubleSpinBox()
        self.deadzone.setRange(0,.95)
        self.deadzone.setSingleStep(.01)
        self.deadzone.setValue(self.p['deadzone'])
        self.deadzone.valueChanged.connect(self.dz_changed)
        dz.addStretch();dz.addWidget(self.deadzone)
        al.addLayout(dz)
        controls_grid.addWidget(axes,0,0)
        triggers,tl=self.panel('triggerGroup',8)
        tl.setAlignment(Qt.AlignmentFlag.AlignTop)
        tl.addWidget(label('04  THROTTLE & BRAKE','triggerHeading'))
        self.mapping_rows(tl,('LT','RT'))
        tl.addWidget(label('Combined LT + RT','sectionTitle'))
        self.combo_label=label('No combined-trigger button assigned','muted')
        self.combo_label.setWordWrap(True)
        tl.addWidget(self.combo_label)
        controls_grid.addWidget(triggers,0,1)
        preview,pr=self.panel('previewGroup',12)
        pr.addWidget(label('MAPPED OUTPUT PREVIEW','eyebrow'))
        self.preview=label('Waiting for input…')
        self.preview.setWordWrap(True)
        pr.addWidget(self.preview)
        self.preview_dialog=QDialog(self);self.preview_dialog.setWindowTitle('Live mapped output')
        preview_layout=QVBoxLayout(self.preview_dialog);preview_layout.addWidget(preview)
        split.addWidget(left)

        photo_card,pl=self.panel('physicalCard',8)
        photo_card.setMinimumWidth(350)
        self.card_header(pl,'LIVE HARDWARE','Original VelocityOne V1','Original V1 layout • click a marker to identify its input.')
        self.view=ControllerView(ASSETS/'v1-front.png')
        self.view.selected.connect(self.region_clicked)
        view_row=QHBoxLayout()
        self.view_mode=QComboBox()
        self.view_mode.addItems(['Front / face-on','Top / base buttons'])
        self.view_mode.currentIndexChanged.connect(self.view.set_view)
        view_row.addWidget(self.view_mode,1)
        view_row.addWidget(button('Identify controls…',self.identify_controls))
        pl.addLayout(view_row)
        pl.addWidget(self.view,1)
        self.region_info=label('','muted')
        self.region_info.setWordWrap(True)
        self.view_mode.currentIndexChanged.connect(lambda index:self.region_info.setText(
            'Face-on view • Select Top to access the base buttons.' if index==0 else
            'Top view • Live grip, lever and base-button activity.'))
        self.view_mode.setCurrentIndex(1)
        pl.addWidget(self.region_info)
        split.addWidget(photo_card)

        actions,ac=self.panel('buttonGroup',5)
        ac.setAlignment(Qt.AlignmentFlag.AlignTop)
        ac.addWidget(label('05  ACTION BUTTONS','buttonHeading'))
        self.mapping_rows(ac,('A','B','X','Y','LB','RB','L3','R3'),4)
        controls_grid.addWidget(actions,1,0,1,2)
        navigation,nl=self.panel('buttonGroup',5)
        nl.setAlignment(Qt.AlignmentFlag.AlignTop)
        nl.addWidget(label('06  NAVIGATION & HAT','buttonHeading'))
        self.mapping_rows(nl,('Menu','View','Guide','Up','Down','Left','Right'),4)
        controls_grid.addWidget(navigation,2,0,1,2)
        split.setSizes([790,720])
        split.setStretchFactor(0,1);split.setStretchFactor(1,1)

        # Secondary editors keep advanced tasks available without crowding the dashboard.
        self.desktop_dialog=QDialog(self)
        self.desktop_dialog.setWindowTitle('Keyboard & mouse bindings')
        self.desktop_dialog.resize(700,560)
        desktop_layout=QVBoxLayout(self.desktop_dialog)
        self.build_desktop(desktop_layout)
        self.graphics_dialog=QDialog(self)
        self.graphics_dialog.setWindowTitle('V1 graphic input assignments')
        self.graphics_dialog.resize(620,700)
        graphics_layout=QVBoxLayout(self.graphics_dialog)
        area,box=self.scroll_page()
        self.build_physical(box)
        graphics_layout.addWidget(area)

        bottom,bl=self.panel('rawCard',6)
        bh=QHBoxLayout()
        bh.addWidget(label('LIVE INPUT MONITOR','eyebrow'))
        bh.addWidget(label('Raw axes & numbered buttons','muted'))
        bh.addStretch()
        self.hat=label('Hat: centered','muted')
        bh.addWidget(self.hat)
        bl.addLayout(bh)
        self.meters=AxisMeter()
        bl.addWidget(self.meters)
        self.button_lights=ButtonMonitor()
        bl.addWidget(self.button_lights)
        content.addWidget(bottom)
        self.status=label('Output stopped','status')
        self.status.setWordWrap(True)
        footer=QHBoxLayout()
        footer.addWidget(self.status,1)
        content.addLayout(footer)
        self.build_menus()
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)
        self.refresh()
        self._baseline=self.profile_signature()

    @staticmethod
    def panel(name,padding=12):
        frame=QFrame()
        frame.setObjectName(name)
        box=QVBoxLayout(frame)
        padding=min(padding,8)
        box.setContentsMargins(padding,padding,padding,padding)
        box.setSpacing(4)
        return frame,box

    @staticmethod
    def card_header(layout,kicker,title,subtitle):
        layout.addWidget(label(kicker,'eyebrow'))
        layout.addWidget(label(title,'sectionTitle'))
        text=label(subtitle,'muted')
        text.setWordWrap(True)
        layout.addWidget(text)

    def scroll_page(self):
        area=QScrollArea()
        area.setWidgetResizable(True)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        w=QWidget()
        box=QVBoxLayout(w)
        box.setContentsMargins(2,2,2,2)
        box.setSpacing(6)
        area.setWidget(w)
        return area,box

    def build_menus(self):
        files=self.menuBar().addMenu('&File')
        save=files.addAction('Save preset',self.save_profile);save.setShortcut('Ctrl+S')
        files.addAction('New preset',self.new_profile)
        files.addAction('Rename preset…',self.rename_profile)
        files.addAction('Import preset…',self.import_profile)
        files.addAction('Open profile folder',lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(ROOT/'profiles'))))
        files.addSeparator();files.addAction('Exit',self.close)
        mappings=self.menuBar().addMenu('&Mappings')
        mappings.addAction('Keyboard / mouse…',lambda:self.open_editor(self.desktop_dialog))
        mappings.addAction('Graphic inputs…',lambda:self.open_editor(self.graphics_dialog))
        mappings.addAction(self.macro_button)
        mappings.addSeparator()
        mappings.addAction('Learn combined LT + RT button…',self.learn_combo)
        mappings.addAction('Clear combined LT + RT button',self.clear_combo)
        output=self.menuBar().addMenu('&Output')
        output.addAction('Live mapped output…',self.preview_dialog.show)
        output.addAction('Start output',self.start_output)
        output.addAction('Stop output',self.stop).setShortcut('Ctrl+Alt+F12')
        tools=self.menuBar().addMenu('&Tools')
        tools.addAction('Identify / calibrate controls…',self.identify_controls)
        tools.addAction('Windows controller test',lambda:subprocess.Popen(['control.exe','joy.cpl']))
        tools.addAction('Driver setup / dependencies…',self.show_dependencies)
        help_menu=self.menuBar().addMenu('&Help')
        help_menu.addAction('Game setup / binding guide…',self.show_game_guide)
        help_menu.addAction('Thumbwheel setup…',lambda:QMessageBox.information(self,'Thumbwheel digital inputs',THUMBWHEEL_SETUP))

    def rename_profile(self):
        name,ok=QInputDialog.getText(self,'Rename preset','Preset name:',text=self.name.text())
        if ok and name.strip():self.name.setText(name.strip()[:80]);self.p['name']=self.name.text()

    def set_action_label(self,target,text):
        self.p.setdefault('target_roles',{})[target]=text.strip()[:80]

    def sync_action_labels(self):
        # textEdited excludes programmatic/UI Automation changes; read the editors
        # at transaction boundaries as well, without disturbing normal typing.
        for target,editor in getattr(self,'target_labels',{}).items():
            self.p.setdefault('target_roles',{})[target]=editor.text().strip()[:80]

    def update_symbol_visibility(self,*_):
        visible=self.mode.currentText()=='Xbox gamepad'
        for symbol in self.target_symbols.values():symbol.setVisible(visible)

    def edit_macros(self):
        self.stop()
        dialog=MacroDialog(self.p.get('macros',[]),self.provider,KEYS,self)
        if dialog.exec():
            self.p['macros']=dialog.macros
            self.refresh()
            saved=self.save_profile()
            self.notice.setText(f"{len(dialog.macros)} macros assigned"+(' and saved. ' if saved else '; save failed. ')+"Start output to enable them. Stop output cancels all macros.")
        dialog.deleteLater()

    def open_editor(self,dialog):
        self.stop()
        dialog.exec()

    def mapping_rows(self,layout,targets,columns=1):
        """Shared mapping controls; only presentation changes between rows and tiles."""
        names={'LX':'Roll','LY':'Pitch','RX':'Camera X','RY':'Camera Y','LT':'Brake','RT':'Throttle'}
        grid=QGridLayout();grid.setContentsMargins(0,0,0,0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(3)
        for index,target in enumerate(targets):
            cell=QVBoxLayout() if columns>1 else QHBoxLayout()
            cell.setSpacing(1);cell.setContentsMargins(0,0,0,0)
            name_row=QHBoxLayout();name_row.setSpacing(3);name_row.setContentsMargins(0,0,0,0)
            symbol=XboxSymbol(target);self.target_symbols[target]=symbol
            name_row.addWidget(symbol)
            title=QLineEdit(names.get(target,target));title.setObjectName('actionName')
            title.setMaxLength(80);title.setMinimumWidth(0);title.setFixedHeight(18)
            title.setPlaceholderText('Game action…')
            title.setToolTip('Edit the game action name; Save preset (Ctrl+S) retains it. Binding is unchanged.')
            title.textEdited.connect(lambda text,t=target:self.set_action_label(t,text))
            self.target_labels[target]=title
            name_row.addWidget(title,1)
            if columns==1:
                name_widget=QWidget();name_widget.setLayout(name_row);name_widget.setFixedWidth(145)
                cell.addWidget(name_widget)
            else:cell.addLayout(name_row)
            controls=QHBoxLayout();controls.setContentsMargins(0,0,0,0)
            controls.setSpacing(3)
            assignment=AxisAssignmentButton('') if target in AXES else QPushButton('')
            assignment.clicked.connect(lambda checked=False,t=target:self.map_output(t))
            assignment.setMinimumWidth(0);assignment.setFixedHeight(24)
            assignment.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Fixed)
            assignment.setToolTip('Learn or edit the physical input for '+target)
            controls.addWidget(assignment,1)
            clear=button('×',lambda checked=False,t=target:self.clear_output(t),'clear')
            clear.setFixedSize(20,24)
            clear.setToolTip('Remove '+target+' assignment')
            controls.addWidget(clear)
            cell.addLayout(controls,1) if columns==1 else cell.addLayout(controls)
            grid.addLayout(cell,index//columns,index%columns)
            self.rows[target]=assignment
        for col in range(columns):grid.setColumnStretch(col,1)
        layout.addLayout(grid)

    def build_desktop(self,l):
        n=label('Choose Keyboard / mouse output in the top bar.\nBindings remain saved alongside your gamepad mapping.\nFor a key chord, bind each key to the same input.','muted');n.setWordWrap(True);l.addWidget(n)
        row=QHBoxLayout();row.addWidget(button('+ Keyboard binding',lambda:self.add_desktop('keys')));row.addWidget(button('+ Mouse binding',lambda:self.add_desktop('mouse')));l.addLayout(row)
        self.desktop_list=QVBoxLayout();l.addLayout(self.desktop_list);l.addStretch()
    def build_physical(self,l):
        n=label('Identify controls on the original V1 image. These assignments drive the live graphics, not game output.\nHidden controls can be identified from this list. OLED area is an illustrative reference.','muted');n.setWordWrap(True);l.addWidget(n)
        self.graphic_buttons={}
        for key,(name,_) in REGIONS.items():
            control=button(name,lambda checked=False,k=key:self.region_clicked(k))
            l.addWidget(control);self.graphic_buttons[key]=control
        for key,name in [('H2_x','H2 horizontal axis'),('H2_y','H2 vertical axis')]:
            l.addWidget(button(name,lambda checked=False,k=key:self.region_clicked(k)))
        l.addStretch()
    def provider(self):return self.state
    def identify_controls(self):
        self.stop()
        dialog=CalibrationDialog(self.provider,self)
        if dialog.exec():
            try:
                self.p=apply_calibration(self.p,dialog.session.sources,dialog.standard.isChecked())
                self.refresh();saved=self.save_profile()
                self.notice.setText('V1 controls identified'+(' and saved.' if saved else '; profile save failed.')+' Verify each lever and H2 before starting output.')
            except (ValueError,KeyError) as e:QMessageBox.warning(self,'Identification not applied',str(e))
    def stop(self):self.engine.stop()
    def start_output(self):
        if self.state is None:QMessageBox.warning(self,'V1 not connected','Connect the original Flightstick in PC mode.');return
        if self.mode.currentText()=='Xbox gamepad' and not self.usbip_present():
            QMessageBox.information(self,'USBIP driver required','Install the signed USBIP driver using Driver setup, then restart Windows if requested. No ViGEm is used.');return
        self.engine.start(self.mode.currentText())
    def usbip_present(self):
        import shutil
        return bool(shutil.which('usbip') or any((pathlib.Path(os.environ.get('ProgramFiles','C:/Program Files'))/p).exists() for p in ('USBip/usbip.exe','USBip/bin/usbip.exe')))
    def show_dependencies(self):
        d=QDialog(self);d.setWindowTitle('Bundled components & driver setup');d.resize(650,500)
        layout=QVBoxLayout(d)
        layout.addWidget(label('Self-contained Windows app','title'))
        text=label('Included inside the EXE: Python runtime, Qt / PySide6, SDL / pygame, V1 images, game presets, VIIPER backend, signed USBIP driver installer, dependency notices and application source. No Python or pip installation is needed.','muted')
        text.setWordWrap(True);layout.addWidget(text)
        for name,path in [('VIIPER 0.9.0',RESOURCE_ROOT/'backend'/'viiper.exe'),('USBIP 0.9.8.1 signed installer',RESOURCE_ROOT/'backend'/'USBip-0.9.8.1-x64.exe')]:
            layout.addWidget(label(('Bundled: ' if path.is_file() else 'MISSING: ')+name))
        note=label('Windows must install the included USBIP driver once, with administrator approval. Restart Windows if the installer asks. Bundled does not mean installed; gamepad attachment must still be checked in Windows input test.','notice')
        note.setWordWrap(True);layout.addWidget(note)
        layout.addWidget(button('Install included USBIP driver…',self.install_driver,'primary'))
        layout.addWidget(button('Export bundled source, backend & notices…',self.export_support))
        layout.addWidget(button('Open profiles and logs folder',lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(ROOT)))))
        layout.addStretch()
        close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);close.rejected.connect(d.reject);layout.addWidget(close)
        d.exec();d.deleteLater()

    def export_support(self):
        import zipfile
        path,_=QFileDialog.getSaveFileName(self,'Export bundled support files',str(ROOT/'VelocityOneMapper-support.zip'),'ZIP archive (*.zip)')
        if not path:return
        try:
            with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
                for folder in ('source','backend','licenses','docs','assets'):
                    for file in (RESOURCE_ROOT/folder).rglob('*'):
                        if file.is_file():archive.write(file,file.relative_to(RESOURCE_ROOT/'source') if folder=='source' else file.relative_to(RESOURCE_ROOT))
                for name in ('THIRD_PARTY.md','README.md'):
                    file=RESOURCE_ROOT/name
                    if file.is_file():archive.write(file,name)
            self.notice.setText('Exported bundled support files to '+path)
        except OSError as e:QMessageBox.warning(self,'Export failed',str(e))

    def install_driver(self):
        self.stop()
        try:exe=stage_driver_installer(RESOURCE_ROOT,ROOT)
        except OSError as e:QMessageBox.warning(self,'Installer unavailable',str(e));return
        if QMessageBox.question(self,'Install signed USBIP driver','This opens the upstream USBIP installer. It changes Windows drivers, asks for administrator approval, and may require a reboot. Continue?')==QMessageBox.StandardButton.Yes:
            result=ctypes.windll.shell32.ShellExecuteW(None,'open',str(exe),None,str(exe.parent),1)
            if result<=32:QMessageBox.warning(self,'Installer did not start',f'Windows error {result}')
    def map_output(self,target):
        self.stop();src=self.p['outputs'].get(target)
        d=OutputInputsDialog(f'Map {target}',self.provider,src,self,output_target=target)
        if d.exec():
            source=d.source()
            if source is None:self.p['outputs'].pop(target,None)
            else:self.p['outputs'][target]=source
            self.refresh()
        d.deleteLater()
    def clear_output(self,target):self.stop();self.p['outputs'].pop(target,None);self.refresh()
    def learn_combo(self):
        self.stop();d=SourceDialog('Combined LT + RT button',self.provider,{'kind':'button','index':self.p['combo']} if self.p['combo'] is not None else None,self,True)
        if d.exec():self.p['combo']=d.source()['index'];self.refresh()
    def clear_combo(self):self.stop();self.p['combo']=None;self.refresh()
    def region_clicked(self,key):
        self.stop();name=REGIONS[key][0] if key in REGIONS else {'H2_x':'H2 horizontal axis','H2_y':'H2 vertical axis'}[key];self.region_info.setText(name+' • '+source_text(self.p['physical'].get(key)))
        d=SourceDialog('Identify physical '+name,self.provider,self.p['physical'].get(key),self,button_only=key.startswith(('system_','slider_end_')))
        if key.startswith('system_'):
            d.notice.setText('Click Learn, then press this button. If Windows does not expose it as a joystick input, no capture will appear. Do not assign a guessed number.')
        if key.startswith('lever') and key not in self.p['physical']:d.range.setCurrentText('full')
        if d.exec():self.p['physical'][key]=d.source();self.refresh()
    def dz_changed(self,v):self.stop();self.p['deadzone']=v
    def add_desktop(self,kind):
        self.stop();d=SourceDialog('Choose input for '+('key' if kind=='keys' else 'mouse'),self.provider,None,self)
        if not d.exec():return
        source=d.source()
        dialog=QDialog(self);dialog.setWindowTitle('Choose '+kind+' output');form=QFormLayout(dialog);choice=QComboBox()
        choice.addItems(list(KEYS) if kind=='keys' else ['x','y','left','right','middle']);form.addRow('Output',choice)
        speed=QSpinBox();speed.setRange(1,3000);speed.setValue(600)
        if kind=='mouse':form.addRow('Pixels / second at full travel',speed)
        bb=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);bb.accepted.connect(dialog.accept);bb.rejected.connect(dialog.reject);form.addRow(bb)
        if dialog.exec():
            b={'source':source}
            if kind=='keys':b.update(vk=KEYS[choice.currentText()],label=choice.currentText())
            else:b.update(action=choice.currentText(),speed=speed.value())
            self.p[kind].append(b);self.refresh()
        dialog.deleteLater()
    def remove_desktop(self,kind,index):self.stop();self.p[kind].pop(index);self.refresh()
    def refresh(self):
        for key,control in getattr(self,'graphic_buttons',{}).items():
            if key.startswith('front_'):control.hide()
            elif key.startswith('system_'):control.show()
        roles=self.p.get('target_roles',{})
        default_names={'LX':'Roll','LY':'Pitch','RX':'Camera X','RY':'Camera Y','LT':'Brake','RT':'Throttle'}
        for target,title in self.target_labels.items():
            role=roles.get(target,default_names.get(target,''))
            title.setText(role or target);title.setCursorPosition(0)
            title.setToolTip('Edit game action: '+(role or target)+' • '+target+' • Save preset with Ctrl+S')
        self.macro_button.setText(f"Macros ({len(self.p.get('macros',[]))})…")
        for t,b in self.rows.items():
            text=source_text(self.p['outputs'].get(t));b.setProperty('mappingText',text);b.setText(text);b.setToolTip(text+' - click to edit physical inputs')
        self.update_assignment_activity(evaluate(self.p,self.state))
        c=self.p.get('combo');self.combo_label.setText('Unassigned • set via Mappings menu' if c is None else f'Button {c+1} → LT + RT • release restores levers')
        while self.desktop_list.count():
            item=self.desktop_list.takeAt(0)
            if item.widget():item.widget().deleteLater()
        for kind in ('keys','mouse'):
            for i,b in enumerate(self.p[kind]):
                text=source_text(b['source'])+' → '+b.get('label',b.get('action',''))
                w=button(text+'   ×',lambda checked=False,k=kind,n=i:self.remove_desktop(k,n));w.setToolTip('Click to remove this binding');self.desktop_list.addWidget(w)
        self.view.profile=self.p
        self.update_symbol_visibility()
    def profile_signature(self):
        self.sync_action_labels()
        p=dict(self.p,name=self.name.text().strip(),mode=self.mode.currentText())
        return json.dumps(p,sort_keys=True,ensure_ascii=False)

    def save_pending(self):
        if not self.has_pending_changes():return True
        return self._save_profile(update_browser=False)

    def has_pending_changes(self):
        return self._baseline is not None and self.profile_signature()!=self._baseline

    def reload_profiles(self,game=None):
        game=game or self.p.get('game',CUSTOM_GAME)
        entries=list_presets(ROOT/'profiles')
        games=sorted(set(GAMES)|{CUSTOM_GAME,game}|{p.get('game',CUSTOM_GAME) for p,_ in entries})
        self.game_selector.blockSignals(True)
        self.game_selector.clear();self.game_selector.addItems(games)
        self.game_selector.setCurrentText(game);self.game_selector.blockSignals(False)
        self.profiles.blockSignals(True);self.profiles.clear()
        self.profiles.addItem('Choose user preset / starter…',None)
        for preset_id in starter_ids(game):
            self.profiles.addItem('Starter · '+starter_name(game,preset_id),dict(type='builtin',game=game,id=preset_id))
            if self.current_path is None and self.p.get('game')==game and self.p.get('preset_id')==preset_id:self.profiles.setCurrentIndex(self.profiles.count()-1)
        for p,path in entries:
            if p.get('game',CUSTOM_GAME)==game:
                self.profiles.addItem('User · '+p['name'],dict(type='user',path=str(path)))
                if self.current_path and path.resolve()==pathlib.Path(self.current_path).resolve():self.profiles.setCurrentIndex(self.profiles.count()-1)
        self.profiles.blockSignals(False)

    def save_profile(self):return self._save_profile(update_browser=True)

    def _save_profile(self,update_browser=True):
        self.sync_action_labels()
        self.p['name']=self.name.text().strip();self.p['mode']=self.mode.currentText()
        self.p.setdefault('game',CUSTOM_GAME)
        try:
            path=save_preset(ROOT/'profiles',self.p,replace_path=self.current_path)
            self.current_path=path;self._baseline=self.profile_signature();self.remember_profile(path)
            if update_browser:self.reload_profiles()
            self.notice.setText('Saved '+self.p['game']+' / '+self.p['name'])
            return True
        except (ValueError,OSError,KeyError,TypeError) as e:
            QMessageBox.warning(self,'Cannot save preset',str(e));return False

    def remember_profile(self,path):
        if not path:return
        try:
            relative=pathlib.Path(path).resolve().relative_to((ROOT/'profiles').resolve())
            temp=ROOT/'state.tmp';temp.write_text(json.dumps(dict(last_profile=str(relative))),encoding='utf-8');temp.replace(ROOT/'state.json')
        except (OSError,ValueError):pass

    def restore_profile(self):
        try:
            state=ROOT/'state.json'
            if state.is_file() and state.stat().st_size<65536:
                saved=json.loads(state.read_text(encoding='utf-8'))
                if not isinstance(saved,dict):raise ValueError('Invalid saved selection')
                relative=saved.get('last_profile')
                path=(ROOT/'profiles'/relative).resolve()
                if path.is_relative_to((ROOT/'profiles').resolve()) and path.is_file():
                    if self.load_path(path,save_pending=False):return
        except (OSError,ValueError,TypeError):pass
        entries=list_presets(ROOT/'profiles')
        if entries:self.load_path(max(entries,key=lambda entry:entry[1].stat().st_mtime_ns)[1],save_pending=False)

    def activate_profile(self,p,message,path=None):
        p=upgrade_legacy_action_labels(p)
        self.p=p;self.current_path=path
        self.name.setText(p['name']);self.mode.setCurrentText(p.get('mode','Xbox gamepad'))
        blocked=self.deadzone.blockSignals(True)
        try:self.deadzone.setValue(p['deadzone'])
        finally:self.deadzone.blockSignals(blocked)
        self.refresh();self.reload_profiles()
        self._baseline=self.profile_signature();self.notice.setText(message);self.remember_profile(path)

    def load_path(self,path,save_pending=True):
        self.stop()
        if save_pending and not self.save_pending():return False
        try:
            path=pathlib.Path(path)
            if path.stat().st_size>1_000_000:raise ValueError('Profile is too large')
            p=validate_profile(json.loads(path.read_text(encoding='utf-8')))
            p,legacy=clear_unverified_levers(p);p=apply_reported_layout(p);p.setdefault('game',CUSTOM_GAME)
            message='Loaded '+p['game']+' / '+p['name']+' • output stopped'
            if legacy:message+=' • legacy lever guesses removed; verify the measured axes.'
            self.activate_profile(p,message,path);return True
        except (ValueError,OSError,KeyError,TypeError) as e:
            QMessageBox.warning(self,'Invalid preset',str(e));return False

    def load_selected(self,index,save_pending=True):
        data=self.profiles.itemData(index)
        if not data:return
        self.stop()
        if save_pending and not self.save_pending():self.reload_profiles();return
        if data['type']=='user':self.load_path(data['path']);return
        game=data['game'];preset_id=data['id']
        p=make_starter(game,preset_id,self.p)
        self.activate_profile(p,'STARTER • '+game+' / '+p['name']+' • unverified in-game; review Game setup before output.')
        for i in range(self.profiles.count()):
            if self.profiles.itemData(i)==data:self.profiles.setCurrentIndex(i);break

    def custom_game_finished(self):
        game=self.game_selector.currentText().strip()
        if game!=self.p.get('game',CUSTOM_GAME):self.game_changed()

    def game_changed(self,*_):
        game=self.game_selector.currentText().strip()
        if not game or len(game)>120:self.reload_profiles();return
        if game==self.p.get('game',CUSTOM_GAME):return
        self.stop()
        if not self.save_pending():self.reload_profiles();return
        self.current_path=None;self.reload_profiles(game)
        indices=[i for i in range(1,self.profiles.count()) if (self.profiles.itemData(i) or {}).get('type')=='user']
        index=indices[0] if indices else 1 if self.profiles.count()>1 else None
        if index is not None:
            self.profiles.setCurrentIndex(index);self.load_selected(index,False)
        else:self.new_profile_for_game(game)

    def new_profile_for_game(self,game):
        physical=self.p.get('physical',{})
        p=apply_reported_layout(default_profile());p['physical'].update(physical)
        p.update(game=game,name='New user preset',outputs={})
        if self.p.get('calibration_version')==1:p['calibration_version']=1
        self.activate_profile(p,'New blank preset for '+game+' • assign controls, name it and Save.')

    def new_profile(self):
        game=self.game_selector.currentText().strip() or CUSTOM_GAME
        self.stop()
        if self.save_pending():self.new_profile_for_game(game)

    def import_profile(self):
        self.stop()
        if not self.save_pending():return
        path,_=QFileDialog.getOpenFileName(self,'Import user preset',str(ROOT),'Profiles (*.json)')
        if path:self.load_path(path)

    def show_game_guide(self):
        game=self.p.get('game',CUSTOM_GAME);entry=GAMES.get(game)
        d=QDialog(self);d.setWindowTitle(game+' • setup guide');d.resize(850,760)
        layout=QVBoxLayout(d)
        layout.addWidget(label(game,'sectionTitle'))
        note=label('Suggested starter layout • not factory defaults or verified game compatibility. Bind or remap the outputs below in the game.','notice')
        note.setWordWrap(True);layout.addWidget(note)
        steps=label((entry['setup'] if entry else 'Configure this custom game using its own controller settings.')+
            '\nStart Xbox output and confirm the virtual controller in Windows before binding in-game. The app does not import or overwrite game configuration files.','muted')
        steps.setWordWrap(True);layout.addWidget(steps)
        wheel=label('Thumbwheel setup: '+THUMBWHEEL_SETUP,'notice');wheel.setWordWrap(True);layout.addWidget(wheel)
        table=QTableWidget(0,3);table.setHorizontalHeaderLabels(['Virtual output','V1 input','Suggested in-game action'])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for target,src in self.p['outputs'].items():
            row=table.rowCount();table.insertRow(row)
            for col,text in enumerate((target,source_text(src),self.p.get('target_roles',{}).get(target,'Choose in game'))):
                table.setItem(row,col,QTableWidgetItem(text))
        layout.addWidget(table,1)
        limit=label('This virtual controller has four signed stick axes and two one-way triggers. Full native-HOTAS setups can use the original stick directly in supported games with mapper output stopped. Starter layouts do not assign every aircraft/ship function.','muted')
        limit.setWordWrap(True);layout.addWidget(limit)
        if entry:layout.addWidget(button('Open official game / controls reference',lambda:QDesktopServices.openUrl(QUrl(entry['url']))))
        close=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);close.rejected.connect(d.reject);layout.addWidget(close)
        d.exec();d.deleteLater()

    def update_assignment_activity(self,out):
        # Display the same evaluated values as the gamepad preview, including
        # inversion, dead zone and the combined-trigger override while stopped.
        for target in (*BUTTONS,*AXES):
            control=self.rows.get(target)
            if control is None:continue
            if target in BUTTONS:active=bool(out['buttons']&BUTTONS[target])
            else:
                value=out[target];active=abs(value)>.001
                if hasattr(control,'set_live_value'):
                    control.set_live_value(None if control.property('mappingText')=='Unassigned' else value,target not in ('LT','RT'))
                base=control.property('mappingText')
                if base is None:
                    base=control.text();control.setProperty('mappingText',base)
                reading=f'{value:.0%}' if target in ('LT','RT') else f'{value:+.2f}'
                display=base.replace(' · signed','')
                text=base if base=='Unassigned' else f'{display}  |  {reading}'
                control.setToolTip('Learn or edit '+target+': '+base+' • live '+reading)
                if control.text()!=text:control.setText(text)
            if control.property('liveActive') is active:continue
            control.setProperty('liveActive',active)
            control.style().unpolish(control)
            control.style().polish(control)
            control.update()

    def tick(self):
        if self.closing:return
        self.state=self.device.poll();self.view.state=self.state;self.view.profile=self.p;self.view.update()
        self.engine.snapshot(self.p,self.state)
        self.connected.setText('V1 CONNECTED' if self.state else 'V1 DISCONNECTED')
        self.meters.values=self.state['axes'] if self.state else [];self.meters.update()
        if self.state:
            self.button_lights.set_values(self.state['buttons'])
            self.hat.setText('Hat: '+str(self.state['hats'][0] if self.state['hats'] else 'none'))
        else:self.button_lights.set_values(None);self.hat.setText('Hat: —')
        out=evaluate(self.p,self.state)
        self.update_assignment_activity(out)
        self.preview.setText(f"LT {out['LT']:.0%}    RT {out['RT']:.0%}    LX {out['LX']:+.2f}    LY {out['LY']:+.2f}\nButtons: "+(', '.join(k for k,v in BUTTONS.items() if out['buttons']&v) or 'none'))
        self.status.setToolTip(self.preview.text())
        self.status.setText(('ACTIVE  •  ' if self.engine.active else 'STOPPED  •  ')+self.engine.status)
        tone=('#321a23','#ff9aaf','#723448') if self.engine.error else (('#122c25','#73e0b3','#285c48') if self.engine.active else ('#171e28','#a5b6ca','#303c4d'))
        self.status.setStyleSheet(f'background:{tone[0]};color:{tone[1]};border:1px solid {tone[2]};border-radius:6px;padding:9px;')
        self.connected.setStyleSheet('' if self.state else 'background:#321a23;color:#ff9aaf;border:1px solid #723448;')
        self.start_button.setEnabled(self.state is not None and not self.engine.want)
        user=ctypes.windll.user32
        if all(user.GetAsyncKeyState(k)&0x8000 for k in (0x11,0x12,0x7b)):self.stop()
    def closeEvent(self,event):
        if not self.closing:
            if self.has_pending_changes():
                answer=QMessageBox.question(self,'Unsaved preset changes','Save your preset changes before closing?',
                    QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Save)
                if answer==QMessageBox.StandardButton.Cancel or (answer==QMessageBox.StandardButton.Save and not self.save_profile()):
                    event.ignore();return
            self.closing=True;self.timer.stop();self.engine.close();self.device.close()
        event.accept()

def main():
    if '--render' in sys.argv:os.environ['QT_QPA_PLATFORM']='offscreen'
    if sys.platform=='win32' and '--render' not in sys.argv:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('VelocityOneV1.ControlStation')
    app=QApplication(sys.argv)
    app.frame_theme=DarkWindowFrames(app);app.installEventFilter(app.frame_theme)
    app.setStyle('Fusion');app.setStyleSheet(STYLE);app.setFont(QFont('Segoe UI',10))
    if '--render' in sys.argv:
        for font in ('segoeui.ttf','segoeuib.ttf'):
            QFontDatabase.addApplicationFont(str(pathlib.Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/font))
    w=MainWindow()
    w.show() if '--render' in sys.argv else w.showMaximized()
    if '--profile' in sys.argv:
        index=sys.argv.index('--profile')
        if index+1<len(sys.argv):w.load_path(sys.argv[index+1],save_pending=False)
    else:w.restore_profile()
    if '--diagnostics' in sys.argv:
        target=pathlib.Path(sys.argv[sys.argv.index('--diagnostics')+1])
        target.write_text(json.dumps(dict(frozen=FROZEN,data_root=str(ROOT),resource_root=str(RESOURCE_ROOT),bundled={name:(RESOURCE_ROOT/name).is_file() for name in ('backend/viiper.exe','backend/USBip-0.9.8.1-x64.exe','backend/VIIPER-v0.9.0-source.zip','assets/v1-front.png','assets/v1-top.png','source/app.py','THIRD_PARTY.md')}),indent=2),encoding='utf-8')
    if '--identify' in sys.argv:QTimer.singleShot(800,w.identify_controls)
    if '--render' in sys.argv:
        target=pathlib.Path(sys.argv[sys.argv.index('--render')+1])
        def render():w.grab().save(str(target));w.close();app.quit()
        QTimer.singleShot(1200,render)
    return app.exec()

if __name__=='__main__':sys.exit(main())
