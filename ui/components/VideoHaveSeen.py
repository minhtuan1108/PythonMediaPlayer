import sys
import json
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QGridLayout, QTabBar, QMessageBox, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QFrame, \
    QPushButton, QScrollArea, QMenu, QFileDialog
from ui.components.MyMediaPlayer import MyMediaPlayer
from ui.thread.DownloadThread import DownloadThread

class VideoHaveSeen(QFrame):
    def __init__(self,parent):
        super().__init__()
        # Tạo một Tab Bar
        self.parent = parent
        self.tab_bar = QTabBar()
        self.tab_bar.addTab("Local")
        self.tab_bar.addTab("Network")
        self.tab_bar.addTab("Youtube")
        self.tab_bar.tabBarClicked.connect(self.tab_changed)
        self.tab_bar.setStyleSheet("""
                                   /* Tab chưa được chọn */
                                QTabBar::tab {
                                    background-color: white; /* Màu nền của tab */
                                    color: black; /* Màu chữ của tab */
                                    padding: 8px 16px; /* Kích thước padding */
                                    border-top-left-radius: 10px; /* Bo tròn góc trên bên trái */
                                    border-top-right-radius: 10px; /* Bo tròn góc trên bên phải */
                                }

                                /* Tab được chọn */
                                QTabBar::tab:selected {
                                    background-color: gray; /* Màu nền của tab khi được chọn */
                                    color: white; /* Màu chữ của tab khi được chọn */
                                }

                                /* Tab khi được hover */
                                QTabBar::tab:hover {
                                    background-color: #ddd; /* Màu nền của tab khi được hover */
                                }

                                /* Tab được focus */
                                QTabBar::tab:focus {
                                    background-color: #eee; /* Màu nền của tab khi được focus */
                                }

                                   """)

        # Khung chua tab bar
        self.frame_tab = QFrame()
        self.hbox_layout_tab = QHBoxLayout()
        self.frame_tab.setLayout(self.hbox_layout_tab)
        self.hbox_layout_tab.addWidget(self.tab_bar)

        # CSS Frame Tab
        self.frame_tab.setFixedWidth(300)

        # Khung chua danh sach Qhbox layout
        self.frame = QFrame()
        self.frame.setStyleSheet("""
                                 border-radius: 20%;
                                 background-color: white;
                                 """)
        self.frame_layout = QFrame()
        self.frame_layout.setMouseTracking(True)
        self.vbox_layout = QVBoxLayout()

        # khung chua Button
        self.vbox_layout_list = QVBoxLayout()
        self.frame.setLayout(self.vbox_layout)

        # Tạo một QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
                                QScrollArea {
                                background-color: #f0f0f0; /* Màu nền của QScrollArea */
                            }

                            QScrollBar:vertical {
                                background: #f0f0f0; /* Màu nền của thanh cuộn dọc */
                                width: 12px; /* Độ rộng của thanh cuộn dọc */
                                margin: 0px 0px 0px 0px;
                                border-radius: 6px;
                            }

                            QScrollBar::handle:vertical {
                                background: #c0c0c0; /* Màu nền của cần cuộn */
                                min-height: 20px; /* Chiều cao tối thiểu của cần cuộn */
                                border-radius: 6px; /* Đường cong góc của cần cuộn */
                            }

                            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                                background: transparent; /* Màu nền của các nút cuộn */
                                height: 0px; /* Chiều cao của các nút cuộn */
                                subcontrol-origin: margin;
                            }

                            QScrollBar::add-line:vertical {
                                subcontrol-position: bottom; /* Vị trí của nút cuộn dưới */
                            }

                            QScrollBar::sub-line:vertical {
                                subcontrol-position: top; /* Vị trí của nút cuộn trên */
                            }
                                """)

        # self.frame.setLayout(self.scroll_area)
        self.vbox_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.frame_layout)
        self.frame_layout.setLayout(self.vbox_layout_list)

        self.vbox_layout_list.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.frame_tab)
        self.vbox.setSpacing(0)
        self.vbox.addWidget(self.frame)
        self.setLayout(self.vbox)
        # self.central_widget.setLayout(self.layout)
        #  tao label
        self.label = QLabel()

        # Lưu trữ trạng thái của các tab
        self.tab_states = [False, False, False]
        self.selected_url = None
        self.buttons = {}  # Dictionary để lưu trữ các nút theo tab index
        self.filename = ""  # tao value ten json
        self.tab_changed(0)  # Goi chay cung UI khi render UI
        self.index_saved = 0

        # Xử lý sự kiện khi tab được chọn

    def tab_changed(self, index):

        # Loại bỏ layout của các tab khác
        for i, state in enumerate(self.tab_states):
            if i != index and state == True:
                self.remove_layout()

        # Cập nhật trạng thái của tab được chọn
        self.tab_states[index] = True

        text = self.tab_bar.tabText(index)
        if text == "Local":
            self.render_local()
            self.filename = "data/local_file_data.json"
            self.index_saved = 0
        elif text == "Network":
            self.render_network()
            self.filename = "data/http_data.json"
            self.index_saved = 1
        elif text == "Youtube":
            self.render_youtube()
            self.filename = "data/youtube_data.json"
            self.index_saved = 2

            # render giao dien link local

    def render_local(self):
        index = 0
        self.remove_layout()  # Loại bỏ layout cũ (nếu có)
        data = []

        # doc file
        try:
            with open("data/local_file_data.json", "r") as f:
                data = json.load(f)
            print("file ton tai")
            for video in data:
                url = video['url']
                duration = video['duration']
                saved_at = video['saved_at']
                btn_local = QPushButton()
                btn_local.setText(
                    f"{self.shorten_url(url, 45)}\nDuration: {self.changed_time(duration)}\nSaved_at: {saved_at}")
                btn_local.setToolTip(f"{url}")
                btn_local.setIcon(QIcon('./assets/local.png'))
                btn_local.setIconSize(QSize(50, 50))  # Đặt kích thước của biểu tượng
                btn_local.setFixedWidth(400)
                btn_local.setStyleSheet('''
                                    QPushButton {
                                        background-color: #f0f0f0; /* Màu nền */
                                        padding: 10px; /* Khoảng cách nội dung và viền */
                                        font-size: 16px; /* Kích thước font chữ */
                                        text-align:left;
                                        font-family: "Times New Roman";
                                        padding-right: 10px;
                                    }   
                                    QPushButton::hover {
                                        background-color: #e0e0e0; /* Màu nền khi di chuột qua */
                                    }
                                    QPushButton::pressed {
                                        background-color: #d0d0d0; /* Màu nền khi nhấn */
                                    }
                                ''')
                self.vbox_layout_list.addWidget(btn_local)
                btn_local.setProperty("url", url)
                btn_local.setProperty("position", video["position"])
                btn_local.clicked.connect(self.showPopupMenu)

            self.buttons[index] = btn_local
        except Exception as e:
            print("file khong ton tai", e)

        

    # render giao dien link network
    def render_network(self):
        index = 1
        self.remove_layout()  # Loại bỏ layout cũ (nếu có)

        # doc file
        try:
            with open("data/http_data.json", "r") as f:
                data = json.load(f)
            print("file ton tai")
            for video in data:
                url = video['url']
                duration = video['duration']
                saved_at = video['saved_at']

                btn_network = QPushButton()
                btn_network.setText(
                    f"{self.shorten_url(url, 45)}\nDuration: {self.changed_time(duration)}\nSaved_at: {saved_at}")
                btn_network.setToolTip(f"{url}")
                btn_network.setIcon(QIcon('./assets/netword.png'))
                btn_network.setIconSize(QSize(50, 50))
                btn_network.setFixedWidth(400)
                self.vbox_layout_list.addWidget(btn_network)
                btn_network.setStyleSheet("""
                                    QPushButton {
                                        background-color: #f0f0f0; /* Màu nền */
                                        padding: 10px; /* Khoảng cách nội dung và viền */
                                        font-size: 16px; /* Kích thước font chữ */
                                        text-align:left;
                                        font-family: "Times New Roman";
                                        
                                    }
                                    QPushButton:hover {
                                        background-color: #e0e0e0; /* Màu nền khi di chuột qua */
                                    }
                                    QPushButton:pressed {
                                        background-color: #d0d0d0; /* Màu nền khi nhấn */
                                    }
                                """)
                btn_network.setProperty("url", url)
                btn_network.setProperty("position", video["position"])
                btn_network.clicked.connect(self.showPopupMenu)
            self.buttons[index] = btn_network
        except Exception as e:
            print("file khong ton tai", e)

        

    # render giao dien link youtube
    def render_youtube(self):
        index = 2
        self.remove_layout()  # Loại bỏ layout cũ (nếu có)

        # doc file
        try:
            with open("data/youtube_data.json", "r") as f:
                data = json.load(f)
            print("file ton tai")
            for video in data:
                title = video['title'] if video['title'] != '' else video['url']
                duration = video['duration']
                saved_at = video['saved_at']
                btn_youtube = QPushButton()
                btn_youtube.setText(
                    f"{self.shorten_url(title, 45)}\nDuration: {self.changed_time(duration)}\nSaved_at: {saved_at}")
                btn_youtube.setToolTip(f"{title}")
                btn_youtube.setIcon(QIcon('./assets/youtube.png'))
                btn_youtube.setIconSize(QSize(50, 50))
                btn_youtube.setFixedWidth(400)
                self.vbox_layout_list.addWidget(btn_youtube)
                btn_youtube.setStyleSheet("""
                                    QPushButton {
                                        background-color: #f0f0f0; /* Màu nền */
                                        padding: 10px; /* Khoảng cách nội dung và viền */
                                        font-size: 16px; /* Kích thước font chữ */
                                        text-align:left;
                                        font-family: "Times New Roman";
                                    }
                                    QPushButton:hover {
                                        background-color: #e0e0e0; /* Màu nền khi di chuột qua */
                                    }
                                    QPushButton:pressed {
                                        background-color: #d0d0d0; /* Màu nền khi nhấn */
                                    }
                                """)
                btn_youtube.clicked.connect(self.showPopupMenu)
                btn_youtube.setProperty("url", video["url"])
                btn_youtube.setProperty("position", video["position"])
            self.buttons[index] = btn_youtube
        except Exception as e:
            print("file khong ton tai", e)

        

    # Loại bỏ layout của tab khi không được chọn
    def remove_layout(self):
        # Xóa tất cả các widget con của vbox_layout_list
        while self.vbox_layout_list.count() > 0:
            widget = self.vbox_layout_list.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()

        # Xóa các nút từ self.buttons
        self.buttons.clear()

    def showPopupMenu(self):
        # Tạo một menu popup
        self.popup_menu = QMenu(self)
        self.popup_menu.setStyleSheet(
            """
            QMenu {
                background: rgba(98, 98, 98, 90);
                color: white;
                padding: 4px;
            }
            QMenu::item {
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background: rgba(98, 98, 98, 255);
            }
        """
        )
        # Thêm các mục vào menu popup
        self.actionPlay = self.popup_menu.addAction(QIcon("assets/play_green.png"), "Play")
        # self.actionDownload = self.popup_menu.addAction(QIcon("assets/download.png"),"Download")
        if self.index_saved != 0: 
            self.actionDownload = self.popup_menu.addAction(QIcon("assets/download.png"),"Download")
        self.actionDel = self.popup_menu.addAction(QIcon("assets/trash_red.png"), "Delete")
        sender = self.sender()
        self.selected_url = sender.property("url")
        self.position = sender.property("position")
        self.actionPlay.triggered.connect(self.actionPlayer)
        # self.actionDownload.triggered.connect(self.actionDownloadVideo)
        if self.index_saved != 0: 
            self.actionDownload.triggered.connect(self.actionDownloadVideo)
        self.actionDel.triggered.connect(self.actionDelete)
        # Lấy tọa độ của sự kiện chuột và hiển thị menu popup tại vị trí đó
        cursor_pos = QCursor.pos()
        self.popup_menu.exec_(cursor_pos)

    def actionPlayer(self):
        
        print("log position:", self.position)
        index_action = self.index_saved
        text = self.tab_bar.tabText(index_action)
        myurl = self.selected_url
        self.parent.videoContent.media_player.myurl = myurl
        print(myurl)
        if text == "Local":
            self.parent.videoHaveSeen.hide()
            self.parent.videoContent.show()
            self.parent.videoContent.currentPosition = self.parent.videoContent.media_player.position()
            self.parent.videoContent.currentDuration = self.parent.videoContent.media_player.duration()
            self.parent.videoContent.media_player.stop()
            self.parent.videoContent.media_player.load_film(myurl)
            self.parent.parent.navBar.on_button_clicked("Now Playing")
            self.newposition = self.get_new_positon()
        elif text == "Network":
            self.parent.videoHaveSeen.hide()
            self.parent.videoContent.show()
            self.parent.videoContent.currentPosition = self.parent.videoContent.media_player.position()
            self.parent.videoContent.currentDuration = self.parent.videoContent.media_player.duration()
            self.parent.videoContent.media_player.stop()
            self.parent.videoContent.media_player.play_from_url(False)
            self.parent.parent.navBar.on_button_clicked("Now Playing")
            self.newposition = self.get_new_positon()
        elif text == "Youtube":
            self.parent.videoHaveSeen.hide()
            self.parent.videoContent.show()
            self.parent.videoContent.currentPosition = self.parent.videoContent.media_player.position()
            self.parent.videoContent.currentDuration = self.parent.videoContent.media_player.duration()
            self.parent.videoContent.media_player.stop()
            self.parent.videoContent.media_player.get_youtube_url()
            self.parent.parent.navBar.on_button_clicked("Now Playing")
            self.newposition = self.get_new_positon()
        if self.parent.videoContent.media_player.state() != QMediaPlayer.StoppedState:
            self.parent.videoContent.set_position(self.newposition)
    
    def get_new_positon(self):
        # Đọc dữ liệu từ tệp
        with open(self.filename, "r") as f:
            data = json.load(f)
        for item in data: 
            if item.get("url") == self.selected_url:
                new_position = item.get("position")
        print("vvvvvvvvvvvvvvvv",new_position)
        return new_position
    
    def actionDownloadVideo(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select folder")
        if folder_path:
            filename = ""
            url = self.selected_url
            if self.index_saved == 1:
                filename = self.parent.get_current_time_as_string("network")
                self.parent.before_download()
                self.thread1 = DownloadThread(url, folder_path, filename, "network")
                self.thread1.finished.connect(self.parent.after_download)      
                self.thread1.start()      
            elif self.index_saved == 2:
                url = self.selected_url
                filename = self.parent.get_current_time_as_string("youtube")
                self.parent.before_download()
                self.thread2 = DownloadThread(url, folder_path, filename, "youtube")
                self.thread2.finished.connect(self.parent.after_download) 
                self.thread2.start()                 
        else:
            print("Folder invalid!")
    
    def actionDelete(self):
        # Yêu cầu xác nhận từ người dùng
        reply = QMessageBox.question(self, 'Thông báo', 'Bạn có chắc muốn xóa?', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        # Đọc dữ liệu từ tệp
        with open(self.filename, "r") as f:
            data = json.load(f)

        print(self.selected_url)

        # Kiểm tra phản hồi của người dùng
        if reply == QMessageBox.Yes:
            print('Đã xóa!')
            # Lọc ra URL đã chọn
            new_data = [item for item in data if item.get("url") != self.selected_url]
            print(new_data)
            # Ghi dữ liệu đã cập nhật vào tệp
            try:
                with open(self.filename, "w") as f:
                    json.dump(new_data, f, indent=7)
                print("Dữ liệu đã được ghi vào tệp thành công.")
            except Exception as e:
                print("Có lỗi xảy ra khi ghi dữ liệu vào tệp:", e)

            # render lai giao dien da xoa
            index = self.index_saved
            self.tab_changed(index)
        else:
            print('Hủy bỏ xóa')
            print(self.selected_url)

    # rut gon url
    def shorten_url(self, url, max_length):
        if len(url) <= max_length:
            return url
        else:
            return url[:max_length - 3] + "..."

    # chuyen thoi gian
    def changed_time(self, duration):
        seconds = duration // 1000
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:02d}"
