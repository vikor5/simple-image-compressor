from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QSlider, QSpinBox, QScrollArea,
    QStatusBar,
    QSpacerItem, QSizePolicy,
    QFileDialog,
    QStyle
)
from PySide6.QtGui import QPixmap, QFont, QPalette, QDrag, QIcon
from PySide6.QtCore import Qt, QMimeData, QPoint, QUrl

import subprocess, os, sys, shutil, json
import glob

import utils, widgets

app = QApplication(sys.argv)

class Widget(QMainWindow):
    def __init__(self):
        super().__init__()
        program_dir = os.path.dirname(sys.argv[0])

        with open("config.json", "r") as file:
            configuration = json.load(file)

        self.default_cmprs_val = configuration["default_compression_value"]
        self.out_img_name_pat = configuration["out_img_name_pat"] # output image name pattern
        load_folder = configuration["load_folder"]
        
        self.scale_factor = 1.0
        self.scale_factor_min = 0.05
        self.scale_factor_max = 20
        
        self.input_img_path = ""
        self.real_pixmap = None
        self.cmprsd_pixmap = None  # compressed image pix map
        self.output_img_path = os.path.join(program_dir,"output/out.jpg")
        self.load_folder = load_folder
        
        self.setWindowTitle("Image Compressor")
        self.setWindowIcon(QIcon(os.path.join(program_dir, "icons/minimize.png")))
        self.setGeometry(100, 100, 1000, 800)
        
        self.init_menubar()
        
        self.setStatusBar(QStatusBar())
        
        self.init_central_widget()
    
    def init_menubar(self):
        self.menu_bar = self.menuBar()
        
        self.file_menu = self.menu_bar.addMenu("File")
        load_action =  self.file_menu.addAction("Open")
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.open_image_with_file_dialog)
        save_action = self.file_menu.addAction("Save")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file_with_file_dialog)
        
        self.view_menu = self.menu_bar.addMenu("View")
        zoom_in_action = self.view_menu.addAction("Zoom In")
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        zoom_out_action = self.view_menu.addAction("Zoom Out")
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
    
    def init_central_widget(self):
        self.central_widget = QWidget()
        
        # Compression layout - the top layout - has input fields for compression
        self.cmprs_panel = widgets.CompressionPanel(default_cmprs_val=self.default_cmprs_val)
        self.cmprs_panel.set_on_value_change(self.compress_image)
        
        # Actual image - this layout has the real image and it's size
        real_image_layout = QVBoxLayout()
        self.real_image_label = QLabel()
        self.real_image_label.setBackgroundRole(QPalette.Base)
        # real image scroll area
        self.real_img_scroll_area = widgets.customScrollArea()
        self.real_img_scroll_area.setWidget(self.real_image_label)
        self.real_img_scroll_area.setWidgetResizable(True)
        real_image_layout.addWidget(self.real_img_scroll_area)
        # real image size label
        self.real_img_size_label = QLabel("Size: ")
        self.real_img_size_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        real_image_layout.addWidget(self.real_img_size_label)
        
        # Compressed image - this layout has the compressed image and it's size
        cmprsd_image_layout = QVBoxLayout()
        self.cmprsd_image_label = QLabel()
        self.cmprsd_image_label.setBackgroundRole(QPalette.Base)
        # compressed image scroll area
        self.cmprsd_img_scroll_area = widgets.customScrollArea()
        self.cmprsd_img_scroll_area.setWidget(self.cmprsd_image_label)
        self.cmprsd_img_scroll_area.setWidgetResizable(True)
        cmprsd_image_layout.addWidget(self.cmprsd_img_scroll_area)
        # compressed image size label
        self.cmprsd_img_size_label = QLabel("Size: ")
        self.cmprsd_img_size_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cmprsd_image_layout.addWidget(self.cmprsd_img_size_label)
        
        # Setting zoom functions for scroll Areas
        self.real_img_scroll_area.set_zoom_funcs(self.zoom_in, self.zoom_out)
        self.cmprsd_img_scroll_area.set_zoom_funcs(self.zoom_in, self.zoom_out)
        
        # Connecting the scroll bars of both the scroll areas
        self.real_img_hor_bar = self.real_img_scroll_area.horizontalScrollBar()
        self.real_img_ver_bar = self.real_img_scroll_area.verticalScrollBar()
        self.cmprsd_img_hor_bar = self.cmprsd_img_scroll_area.horizontalScrollBar()
        self.cmprsd_img_ver_bar = self.cmprsd_img_scroll_area.verticalScrollBar()
        self.cmprsd_img_hor_bar.valueChanged.connect(lambda value: self.real_img_hor_bar.setValue(value))
        self.cmprsd_img_ver_bar.valueChanged.connect(lambda value: self.real_img_ver_bar.setValue(value))
        
        # Combining both images layouts - images_layout
        images_layout = QHBoxLayout()
        images_layout.addLayout(real_image_layout)
        images_layout.addLayout(cmprsd_image_layout)
        images_layout.setSpacing(20)
        
        # Set styles and alignments for both (real and comp) images
        # self.real_image_label.setStyleSheet("QLabel {background-color: grey; border-radius: 0px}")
        self.real_image_label.setAlignment(Qt.AlignCenter)
        # self.cmprsd_image_label.setStyleSheet("QLabel {background-color: grey; border-radius: 0px}")
        self.cmprsd_image_label.setAlignment(Qt.AlignCenter)
        
        # set fonts sizes for size labes
        font16 = QFont()
        font16.setPointSize(16)
        self.real_img_size_label.setFont(font16)
        self.cmprsd_img_size_label.setFont(font16)
        
        
        down_sub_layout = self.init_bottom_btns()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.cmprs_panel)
        main_layout.addLayout(images_layout)
        main_layout.addLayout(down_sub_layout)
        
        self.central_widget.setLayout(main_layout)
        
        self.setCentralWidget(self.central_widget)

    def init_bottom_btns(self):
        """initialize -  bottom buttons"""
        layout = QHBoxLayout()
        load_button = QPushButton("Load")
        load_button.setStatusTip("Load latest image from configured load_folder")
        load_button.setStyleSheet("""QPushButton { background-color: darkblue;}""")
        load_button.clicked.connect(self.load_btn_clicked)
        layout.addWidget(load_button)
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(lambda: utils.copy_image_to_clipboard(self.output_img_path))
        copy_btn.setStatusTip("Copy image to clipboard")
        layout.addWidget(copy_btn)
        # temp_btn = QPushButton("Temp")
        # temp_btn.clicked.connect(self.temp_btn_clicked)
        # layout.addWidget(temp_btn)
        # temp_btn2 = QPushButton("Temp2")
        # temp_btn2.clicked.connect(self.temp_btn2_clicked)
        # layout.addWidget(temp_btn2)
        drag_btn = QPushButton("Drag")
        drag_btn.setStatusTip("Click and drag")
        drag_btn.mousePressEvent = self.drag_btn_clicked
        layout.addWidget(drag_btn)
        drag_btn.setStyleSheet("""QPushButton { background-color: green;}""")

        return layout

    def load_btn_clicked(self):
        """opens latest image from load_folder"""
        latest_image = utils.get_latest_image_from_dir(self.load_folder)
        self.open_image(latest_image)
    
    def open_image_with_file_dialog(self):
        file_dialog = QFileDialog()
        
        # Open the file dialog and get the selected file path
        file_path, _ = file_dialog.getOpenFileName(
            None,            # Parent widget (None means no parent)
            "Open File",     # Dialog title
            "",              # Default directory (empty means current directory)
            "Image Files (*.png *.jpg *.jpeg)"  # File filter
        )
        
        self.open_image(input_file=file_path)
    
    def open_image(self, input_file):
        self.input_img_path = input_file
        input_file_name_wo_ext = utils.get_base_name_wo_ext(self.input_img_path) # input image file name wihtout extensions
        output_file_name = self.out_img_name_pat.replace("*", input_file_name_wo_ext) + ".jpg"
        print("output file name:", output_file_name)
        self.output_img_path = "output/"+output_file_name
        
        # set pixmap to the label
        self.real_pixmap = QPixmap(self.input_img_path)
        self.scale_factor = 1.0
        scaled_pixmap = self.real_pixmap.scaled(self.real_img_scroll_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.real_image_label.setPixmap(scaled_pixmap)
        
        # update the size label
        file_size = os.path.getsize(input_file)
        file_size_str = utils.format_file_size(file_size)
        self.real_img_size_label.setText(file_size_str)
        
        # call compress image function also to update the compressed image
        self.compress_image()
    
    def save_file_with_file_dialog(self):
        # by default opens the parent directory of input image
        default_dir = os.path.dirname(self.input_img_path)
        save_file_path, _ = QFileDialog.getSaveFileName(
            None, 
            "Save File",  # Dialog title
            default_dir,           # Default directory ("" means current directory)
            "Image Files (*.jpg)"  # File filters
        )
        
        if save_file_path: 
            try:
                shutil.copy(self.output_img_path, save_file_path)
                print("Image saved successfully")
            except Exception as e:
                print("Error occured while saving: ", e)
                
        else: print("Save operation cancelled.")
        
    def compress_image(self):
        if (self.real_pixmap==None): return
        # print("compressing")
        # print("input image path: ", self.input_img_path)
        # Call ffmpeg command to compress image
        input_image = self.input_img_path
        output_image = self.output_img_path
        compression_value = str(self.cmprs_panel.value())
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_image,
            '-q:v', compression_value,
            output_image,
            '-y',  # to overwrite without asking permission
            '-loglevel', 'quiet' # to disable the output
        ]
        result = subprocess.run(ffmpeg_command, capture_output=True, text=True)
        
        # update pixmaps
        self.cmprsd_pixmap = QPixmap(output_image)
        self.update_images()
        
        # update the size label
        file_size = os.path.getsize(output_image)
        file_size_str = utils.format_file_size(file_size)
        # here size label has percentage also 
        percent = file_size/os.path.getsize(input_image)*100
        file_size_str += f"  ({percent:.1f}%)"
        self.cmprsd_img_size_label.setText(file_size_str)

    def zoom_in(self, zoom_factor=1.25):
        if (self.real_pixmap==None): return
        if (self.scale_factor*zoom_factor>self.scale_factor_max): return
        self.scale_factor *= zoom_factor
        self.update_images()
        self.adjust_scrollbars(zoom_factor)
    
    def zoom_out(self, zoom_factor=0.8):
        if (self.real_pixmap==None): return
        if (self.scale_factor*zoom_factor<self.scale_factor_min): return
        self.scale_factor *= zoom_factor
        self.update_images()
        self.adjust_scrollbars(zoom_factor)
    
    def update_images(self):
        real_scaled_pixmap = self.real_pixmap.scaled(self.real_img_scroll_area.size()*self.scale_factor, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.real_image_label.setPixmap(real_scaled_pixmap)
        cmprsd_scaled_pixmap = self.cmprsd_pixmap.scaled(self.real_img_scroll_area.size()*self.scale_factor, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.cmprsd_image_label.setPixmap(cmprsd_scaled_pixmap)
    
    def adjust_scrollbars(self, factor):
        for scroll_area in (self.real_img_scroll_area, self.cmprsd_img_scroll_area):
            for scroll_bar in (scroll_area.horizontalScrollBar(), scroll_area.verticalScrollBar()):
                scroll_bar.setValue(scroll_bar.value()*factor + (factor-1)*scroll_bar.pageStep()/2)
    
    def drag_btn_clicked(self, event):
        if event.button() != Qt.LeftButton: return
        
        drag = QDrag(self)
        mime_data = QMimeData()

        # Set the file path as the MIME data
        mime_data.setUrls([QUrl.fromLocalFile(self.output_img_path)])
        drag.setMimeData(mime_data)

        # drag.setHotSpot(QPoint(10, 10))  # Set the hotspot where the mouse pointer will be

        # Start the drag operation
        drag.exec(Qt.CopyAction | Qt.MoveAction)
        
    def temp_btn_clicked(self):
        self.cmprsd_img_scroll_area.set_ver_scroll_bar_val(0.2)
    
    def temp_btn2_clicked(self):
        self.cmprsd_img_scroll_area.set_hor_scroll_bar_val(0.5)
        pass
    
window = Widget()
window.show()

app.exec()