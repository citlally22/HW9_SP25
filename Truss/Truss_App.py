#region imports
from Truss_GUI import Ui_TrussStructuralDesign
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from Truss_Classes import TrussController
import sys
#endregion

#region class definitions
class MainWindow(Ui_TrussStructuralDesign, qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_Open.clicked.connect(self.OpenFile)
        self.spnd_Zoom.valueChanged.connect(self.setZoom)

        self.controller = TrussController()
        self.controller.setDisplayWidgets((self.te_DesignReport, self.le_LinkName, self.le_Node1Name,
                                           self.le_Node2Name, self.le_LinkLength, self.gv_Main))

        self.controller.install_event_filter(self)
        self.gv_Main.setMouseTracking(True)

        self.show()

    def setZoom(self):
        self.gv_Main.resetTransform()
        self.gv_Main.scale(self.spnd_Zoom.value(), self.spnd_Zoom.value())

    def eventFilter(self, obj, event):
        if obj == self.controller.get_scene():
            et = event.type()
            if et == qtc.QEvent.GraphicsSceneMouseMove:
                scenePos = event.scenePos()
                strScene = self.controller.handle_mouse_move(scenePos, self.gv_Main.transform())
                self.lbl_MousePos.setText(strScene)
            if event.type() == qtc.QEvent.GraphicsSceneWheel:
                if event.delta() > 0:
                    self.spnd_Zoom.stepUp()
                else:
                    self.spnd_Zoom.stepDown()
        return super(MainWindow, self).eventFilter(obj, event)

    def OpenFile(self):
        filename = qtw.QFileDialog.getOpenFileName(self)[0]
        print(f"Selected file: {filename}")
        if len(filename) == 0:
            print("No file selected.")
            return
        self.te_Path.setText(filename)
        try:
            with open(filename, 'r') as file:
                data = file.readlines()
                print(f"File contents: {data}")
                self.controller.ImportFromFile(data)
        except Exception as e:
            print(f"Error reading file: {e}")
#endregion

#region function definitions
def Main():
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
#endregion

#region function calls
if __name__ == "__main__":
    Main()
#endregion