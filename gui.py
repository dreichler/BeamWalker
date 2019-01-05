import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtSvg import QGraphicsSvgItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyjones.opticalelements import HalfWavePlate, QuarterWavePlate
from pyjones.polarizations import LinearVertical, get_Poincare_sphere
import random


class OpticalElement(QGraphicsSvgItem):
    def __init__(self, path, parent, beam, element):
        super().__init__(path)
        self.parent = parent
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.beam = beam
        self.element = element


class Beam(QtWidgets.QGraphicsPathItem):
    def __init__(self):
        self.alpha = 100
        self.optical_elements = []
        self.path = QtGui.QPainterPath()
        self.path.moveTo(0, 200)
        self.path.lineTo(600, 200)
        self.path.lineTo(600, 220)
        self.path.lineTo(0, 220)
        self.path.lineTo(0, 200)
        super().__init__(self.path)
        self.setBrush(QtGui.QBrush(QtGui.QColor(200, 50, 0)))
        self.setPen(QtGui.QPen(QtGui.QColor(200, 50, 0)))


class PoincareSphere(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ps = get_Poincare_sphere()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class DrawingView(QtWidgets.QGraphicsView):
    def __init__(self, ps):
        QtWidgets.QGraphicsView.__init__(self)
        self.ps = ps
        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, 500, 500))
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.setScene(self.scene)
        self.beam = Beam()
        self.scene.addItem(self.beam)

        self.beamsplitter = OpticalElement('l2.svg', self.viewport(), self.beam, HalfWavePlate(45))
        self.beamsplitter.setScale(0.6)
        self.beamsplitter.setPos(random.uniform(100, 400), random.uniform(100, 400))
        self.scene.addItem(self.beamsplitter)

        self.beamsplitter = OpticalElement('l4.svg', self.viewport(), self.beam, QuarterWavePlate(45))
        self.beamsplitter.setScale(0.6)
        self.beamsplitter.setPos(random.uniform(100, 400), random.uniform(100, 400))
        self.scene.addItem(self.beamsplitter)

        self.input_polarization = LinearVertical()
        self.output_polarization = LinearVertical()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        optical_elements = sorted(self.beam.collidingItems(), key=lambda x: x.pos().x())
        self.output_polarization = self.input_polarization
        for ele in optical_elements:
            self.output_polarization = ele.element * self.output_polarization

        self.output_polarization.plot(self.ps.ps)
        self.ps.draw()


class TopWidget(QtWidgets.QWidget):
    def __init__(self):
        super(TopWidget, self).__init__()
        hbox = QtWidgets.QHBoxLayout(self)

        ps = PoincareSphere()
        drawing = DrawingView(ps)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        splitter.addWidget(drawing)
        splitter.addWidget(ps)
        splitter.setSizes([300, 300])

        hbox.addWidget(splitter)

        self.setLayout(hbox)
        self.setGeometry(600, 600, 1000, 600)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wid = TopWidget()
    wid.show()
    sys.exit(app.exec_())
