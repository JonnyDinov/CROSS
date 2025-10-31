from typing import Dict, List
import math

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem


class RelationshipGraph(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(self.renderHints() | Qt.Antialiasing)
        self.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333;")
        self.nodes = {}

    def clear_graph(self):
        self.scene.clear()
        self.nodes = {}

    def build_graph(self, nodes: List[str], edges: Dict[str, List[str]]):
        self.clear_graph()
        if not nodes:
            return

        radius = 150
        center_x, center_y = 0, 0
        angle_step = 2 * math.pi / max(len(nodes), 1)

        for index, node in enumerate(nodes):
            angle = angle_step * index
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self._add_node(node, QPointF(x, y))

        pen = QPen(QColor("#7f8c8d"))
        pen.setWidth(2)
        for source, targets in edges.items():
            if source not in self.nodes:
                continue
            for target in targets:
                if target not in self.nodes:
                    continue
                source_item = self.nodes[source]
                target_item = self.nodes[target]
                line = self.scene.addLine(
                    source_item.rect().center().x(),
                    source_item.rect().center().y(),
                    target_item.rect().center().x(),
                    target_item.rect().center().y(),
                    pen,
                )
                line.setZValue(-1)

    def _add_node(self, label: str, position: QPointF):
        size = 80
        node = QGraphicsEllipseItem(-size / 2, -size / 2, size, size)
        node.setPen(QPen(QColor("#3498db")))
        node.setBrush(QBrush(QColor(52, 152, 219, 100)))
        node.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        node.setData(0, label)
        node.setPos(position)
        self.scene.addItem(node)

        text_item = QGraphicsTextItem(label)
        text_item.setDefaultTextColor(QColor("white"))
        text_item.setParentItem(node)
        text_item.setPos(-text_item.boundingRect().width() / 2, -10)

        self.nodes[label] = node

    def selected_node_label(self) -> str:
        for item in self.scene.selectedItems():
            label = item.data(0)
            if label:
                return label
        return ""
