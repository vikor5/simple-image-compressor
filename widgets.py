from PySide6.QtWidgets import (
    QScrollArea, QWidget, QLabel, QSpinBox, QSlider,
    QHBoxLayout
)
from PySide6.QtCore import Qt

class customScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.zoom_in = None
        self.zoom_out = None
    
    def set_zoom_funcs(self, zoom_in, zoom_out):
        self.zoom_in = zoom_in
        self.zoom_out = zoom_out
    
    def setHorScrollBar(self):
        """Set horizontal scroll bar"""
        pass

    def printScroll(self):
        pass
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if event.modifiers() == Qt.ControlModifier:
            if delta>20:
                self.zoom_in()
            if delta<-20:
                self.zoom_out()
        else:
            if delta>20:
                pass
            

class CompressionPanel(QWidget):
    """Horizontal widget. Label, Spinbox, Slider"""
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout() # Main layout
        
        #compression label and some attributes
        cmprs_label = QLabel("Compression: ")
        self.initial_cmprs_value = 5
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
