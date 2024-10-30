from PySide6.QtWidgets import QScrollArea
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
            