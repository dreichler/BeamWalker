import sys
import random
import itertools
from PyQt4 import QtGui, QtCore
from PyQt4.QtSvg import QGraphicsSvgItem
from functools import partial

random.random()
gridSize = 10


class OpticalElement(QGraphicsSvgItem):
    def __init__(self, path, parent):
        super().__init__(path)
        self.parent = parent
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.parent.update()

    def mouseReleaseEvent(self, event):
        rect = self.parent.rect()
        itemsize = self.sceneBoundingRect()
        item_middle_y = int((itemsize.bottom()-itemsize.top())/2)
        item_middle_posy = item_middle_y + itemsize.top()
        item_middle_x = int((itemsize.right()-itemsize.left())/2)
        item_middle_posx = item_middle_x + itemsize.left()
        dist = lambda s, d: (s[0]-d[0])**2+(s[1]-d[1])**2
        grid = itertools.product(range(0, int(rect.right()), gridSize), range(0, int(rect.bottom()), gridSize))
        closest_gridpoint = min(grid, key=partial(dist, (item_middle_posx, item_middle_posy)))
        self.setPos(closest_gridpoint[0]-item_middle_x, closest_gridpoint[1]-item_middle_y)
        super().mouseReleaseEvent(event)


class MyView(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)

        # self.setGeometry(QtCore.QRect(100, 100, 600, 250))

        self.scene = QtGui.QGraphicsScene(self)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, 500, 500))
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragMode(QtGui.QGraphicsView.NoDrag)
        self.setFrameShape(QtGui.QFrame.NoFrame)

        self.setScene(self.scene)

        for i in range(3):
            self.beamsplitter = OpticalElement('symbol_wifi.svg', self.viewport())
            self.beamsplitter.setScale(0.1)
            self.beamsplitter.setPos(random.uniform(100, 400), random.uniform(100, 400))
            self.scene.addItem(self.beamsplitter)
            self.beamsplitter = OpticalElement('symbol_home.svg', self.viewport())
            self.beamsplitter.setScale(0.1)
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

        if event.delta() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        newPos = self.mapToScene(event.pos())

        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view = MyView()
    view.show()
    sys.exit(app.exec_())
