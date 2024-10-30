from PySide6.QtWidgets import QScrollArea, QApplication
from PySide6.QtCore import Qt

def format_file_size(file_size):
    file_size_str = "Size: "
    if (file_size>1048576): # >1MB
        file_size_str += f"{file_size/1048576 :.2f}MB"
    elif (file_size>1024): # >1KB
        file_size_str += f"{file_size/1024 :.2f}KB"
    else:
        file_size_str += f"{file_size :.2f}B"
    return file_size_str


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
            