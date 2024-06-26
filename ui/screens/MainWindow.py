from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget, QVBoxLayout

from ui.screens.MainFrame import MainFrame
from ui.components.NavBar import Nav_Bar

# Main container for all screen
class MediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        # Tạo widget để chứa các thành phần bên trong
        self.central_widget = QWidget()
        self.central_widget.setWindowIcon(QIcon('assets/logo.png'))
        self.central_widget.setStyleSheet("background: black;")
        self.setCentralWidget(self.central_widget)

        # Tạo một layout để chứa các thành phần bên trong
        self.hBoxLayout = QVBoxLayout()
        self.hBoxLayout.setContentsMargins(10, 0, 10, 10)

        # Thêm component cần test vào đây
        self.mainFrame = MainFrame(self)
        self.navBar = Nav_Bar(self)

        self.hBoxLayout.addLayout(self.navBar)
        self.hBoxLayout.addWidget(self.mainFrame)

        self.central_widget.setLayout(self.hBoxLayout)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested[QPoint].connect(self.mainFrame.context_menu_requested)

    def closeEvent(self, a0: QCloseEvent):
        self.mainFrame.close_window_event(a0)