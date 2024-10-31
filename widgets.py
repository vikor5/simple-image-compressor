from PySide6.QtWidgets import (
    QScrollArea, QWidget, QLabel, QSpinBox, QSlider,
    QScrollBar, QPushButton,
    QHBoxLayout
)
from PySide6.QtCore import Qt, QPoint, QMimeData
from PySide6.QtGui import QDrag

class customScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()
        
        self.clicked = False # True when mouse left button is clicked and held
        self.click_mouse_pos = QPoint() # position of mouse button when left clicked
        self.click_scroll_pos = QPoint() # (hor, ver) scroll bars values when left clicked
        
        # TODO: change these and just set ranges for already existing scroll bars for scroll areas
        
        # create hor and ver scroll bars
        self.hor_scroll_bar = QScrollBar(Qt.Horizontal)
        self.ver_scroll_bar = QScrollBar(Qt.Vertical)
        
        # set up ranges for scroll bars
        self.hor_scroll_bar.setMinimum(0)
        self.hor_scroll_bar.setMaximum(100)
        self.ver_scroll_bar.setMinimum(0)
        self.ver_scroll_bar.setMaximum(100)
        
        # set these scroll bars to the scroll area
        self.setHorizontalScrollBar(self.hor_scroll_bar)
        self.setVerticalScrollBar(self.ver_scroll_bar)
        
        self.zoom_in = None
        self.zoom_out = None
    
    def set_zoom_funcs(self, zoom_in, zoom_out):
        self.zoom_in = zoom_in
        self.zoom_out = zoom_out
    
    # -------- set and get methods for normalised positions(0-1) of scroll bars ---------------
    def set_hor_scroll_bar_val(self, nor_pos: float):
        """Set horizontal scroll bar with normalized position(0-1)"""
        # Calculate and set horizontal scrollbar position
        h_min = self.hor_scroll_bar.minimum()
        h_max = self.hor_scroll_bar.maximum()
        h_scroll_value = h_min + (h_max - h_min) * nor_pos
        self.hor_scroll_bar.setValue(h_scroll_value)
    
    def set_ver_scroll_bar_val(self, nor_pos: float):
        """set vertical scroll bar with normalized position(0-1)"""
        # calculate and set vertical scroll position
        v_min = self.ver_scroll_bar.minimum()
        v_max = self.ver_scroll_bar.maximum()
        v_scroll_value = v_min + (v_max - v_min)*nor_pos
        self.ver_scroll_bar.setValue(v_scroll_value)
    
    def get_hor_scroll_bar_val(self):
        """returns a normalised position of horizontal scroll bar"""
        return self.hor_scroll_bar.value()/self.hor_scroll_bar.maximum()
    
    def get_ver_scroll_bar_val(self):
        """returns a normalised position of vertical scroll bar"""
        return self.ver_scroll_bar.value()/self.ver_scroll_bar.maximum()
    
    # -------- END : set and get normalised positions : END ------------------
    
    def wheelEvent(self, event):
        # Here we scroll pageStep/7 value for each scroll of mousewheel (mouse wheel delta = 120)
        xdelta = event.angleDelta().x()
        if xdelta!=0:
            # horzontal scrolling case
            self.hor_scroll_bar.setValue(self.hor_scroll_bar.value()-self.hor_scroll_bar.pageStep()/7*xdelta/120)
            
        ydelta = event.angleDelta().y()
        if event.modifiers() == Qt.ControlModifier:
            if ydelta>20:
                self.zoom_in()
            elif ydelta<-20:
                self.zoom_out()
        # horizontal scrolling case
        elif event.modifiers() == Qt.ShiftModifier:
            # Here we scroll pageStep/7 value for each scroll of mousewheel (mouse wheel delta = 120)
            self.hor_scroll_bar.setValue(self.hor_scroll_bar.value()-self.hor_scroll_bar.pageStep()/7*ydelta/120)
        # vertical scrolling case
        else:
            self.ver_scroll_bar.setValue(self.ver_scroll_bar.value()-self.ver_scroll_bar.pageStep()/7*ydelta/120)
    
    # -------- methods for panning ----------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked = True
            self.click_mouse_pos = event.pos()
            self.click_scroll_pos = QPoint(self.hor_scroll_bar.value(), self.ver_scroll_bar.value())
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.clicked==False: return
        delta = event.pos() - self.click_mouse_pos
        if event.modifiers() == Qt.ShiftModifier:
            delta = delta*4
        self.hor_scroll_bar.setValue(self.click_scroll_pos.x()-delta.x())
        self.ver_scroll_bar.setValue(self.click_scroll_pos.y()-delta.y())
        return super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.clicked = False
        return super().mouseReleaseEvent(event)
    # --------- methods for panning :END ----------------
     
class CompressionPanel(QWidget):
    """Horizontal widget. Label, Spinbox, Slider"""
    def __init__(self, default_cmprs_val=5):
        super().__init__()
        
        layout = QHBoxLayout() # Main layout
        
        #compression label and some attributes
        cmprs_label = QLabel("Compression: ")
        self.initial_cmprs_value = default_cmprs_val
        self.min_cmprs_value = 1
        self.max_cmprs_value = 31

        # compression spinbox
        self.cmprs_spinbox = QSpinBox()
        self.cmprs_spinbox.setMinimum(self.min_cmprs_value)
        self.cmprs_spinbox.setMaximum(self.max_cmprs_value)
        self.cmprs_spinbox.setValue(self.initial_cmprs_value)

        # compression slider
        self.cmprs_slider = QSlider(Qt.Horizontal)
        self.cmprs_slider.setMinimum(self.min_cmprs_value)
        self.cmprs_slider.setMaximum(self.max_cmprs_value)
        self.cmprs_slider.setValue(self.initial_cmprs_value)
        
        # Sync the values in slider and spinbox
        self.cmprs_slider.valueChanged.connect(self.slider_val_changed)
        self.cmprs_spinbox.valueChanged.connect(self.spinbox_val_changed)
        
        layout.addWidget(cmprs_label)
        layout.addWidget(self.cmprs_spinbox)
        layout.addWidget(self.cmprs_slider)
        self.setLayout(layout)
        
        # On value changed
        self.on_value_change_func = None
    
    def spinbox_val_changed(self, value):
        # Block the signal and change the value of slider and unblock the signal
        self.cmprs_slider.blockSignals(True)
        self.cmprs_slider.setValue(value)
        self.cmprs_slider.blockSignals(False)
        self.on_value_change()
    
    def slider_val_changed(self, value):
        self.cmprs_spinbox.blockSignals(True)
        self.cmprs_spinbox.setValue(value)
        self.cmprs_spinbox.blockSignals(False)
        self.on_value_change()
    
    def set_on_value_change(self, func):
        """set a function to call on value change"""
        self.on_value_change_func = func
    
    def on_value_change(self):
        # call the repective function
        self.on_value_change_func()
        
    def value(self):
        """Get compression value"""
        return self.cmprs_slider.value()
