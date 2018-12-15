import sys
import random
import itertools
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtSvg import QGraphicsSvgItem
from functools import partial
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyjones.opticalelements import HalfWavePlate, QuarterWavePlate
from pyjones.polarizations import LinearVertical, get_Poincare_sphere
random.random()
gridSize = 10


class OpticalElement(QGraphicsSvgItem):
    def __init__(self, path, parent, beam, element):
        super().__init__(path)
        self.parent = parent
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.beam = beam
        self.element = element

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.parent.update()

    def mouseReleaseEvent(self, event):
        rect = self.parent.rect()
        itemsize = self.sceneBoundingRect()
        item_middle_y = int((itemsize.bottom() - itemsize.top()) / 2)
        item_middle_posy = item_middle_y + itemsize.top()
        item_middle_x = int((itemsize.right() - itemsize.left()) / 2)
        item_middle_posx = item_middle_x + itemsize.left()
        dist = lambda s, d: (s[0] - d[0]) ** 2 + (s[1] - d[1]) ** 2
        grid = itertools.product(range(0, int(rect.right()), gridSize), range(0, int(rect.bottom()), gridSize))
        closest_gridpoint = min(grid, key=partial(dist, (item_middle_posx, item_middle_posy)))
        self.setPos(closest_gridpoint[0] - item_middle_x, closest_gridpoint[1] - item_middle_y)
        super().mouseReleaseEvent(event)
        self.beam.update_elements()


class Beam(QtWidgets.QGraphicsPathItem):
    def __init__(self):
        self.mpl = get_Poincare_sphere()
        self.alpha = 100
        self.optical_elements = []
        self.path = QtGui.QPainterPath()
        self.path.moveTo(0, 200)
        self.path.lineTo(600, 200)
        self.path.lineTo(600, 220)
        self.path.lineTo(0, 220)
        self.path.lineTo(0, 200)
        super().__init__(self.path)
        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, alpha=self.alpha)))
        self.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0, alpha=self.alpha)))
        self.input_polarization = LinearVertical()
        self.output_polarization = LinearVertical()

    def update_elements(self):
        self.optical_elements = sorted(self.collidingItems(), key=lambda x: x.pos().x())
        self.output_polarization = self.input_polarization
        for ele in self.optical_elements:
            self.output_polarization = ele.element*self.output_polarization
        print(self.output_polarization)


class PoincareSphere(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        import numpy as np
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)

class DrawingView(QtWidgets.QGraphicsView):
    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)
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

        self.beamsplitter = OpticalElement('l2.svg', self.viewport(), self.beam, HalfWavePlate(0))
        self.beamsplitter.setScale(0.6)
        self.beamsplitter.setPos(random.uniform(100, 400), random.uniform(100, 400))
        self.scene.addItem(self.beamsplitter)

        self.beamsplitter = OpticalElement('l4.svg', self.viewport(), self.beam, QuarterWavePlate(0))
        self.beamsplitter.setScale(0.6)
        self.beamsplitter.setPos(random.uniform(100, 400), random.uniform(100, 400))
        self.scene.addItem(self.beamsplitter)


    def drawBackground(self, painter, rect):
        rect = rect.normalized()
        pen = QtGui.QPen()
        painter.setPen(pen)
        for x, y in itertools.product(range(0, int(rect.right()), gridSize), range(0, int(rect.bottom()), gridSize)):
            painter.drawPoint(x, y)

    def wheelEvent(self, event):
        zoomInFactor = 1.1
        zoomOutFactor = 1 / zoomInFactor

        oldPos = self.mapToScene(event.pos())

        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        newPos = self.mapToScene(event.pos())

        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    view = DrawingView()
    view.show()
    sys.exit(app.exec_())

