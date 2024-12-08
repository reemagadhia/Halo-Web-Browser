from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtGui

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Halo Web Browser")
        self.setWindowIcon(QtGui.QIcon('halo.webp'))

        # Create the tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Create a menu bar
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        self.bookmarks_menu = self.menu.addMenu("Bookmarks")
        self.bookmarked_urls = []

        # Add actions to the File menu
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda: self.add_new_tab(QUrl('https://www.google.com'), "New Tab"))
        self.file_menu.addAction(new_tab_action)

        add_bookmark_action = QAction("Add Bookmark", self)
        add_bookmark_action.triggered.connect(self.add_bookmark)
        self.file_menu.addAction(add_bookmark_action)

        # Add the first tab
        self.add_new_tab(QUrl('https://www.google.com'), "New Tab")

    def add_new_tab(self, url, label):
        tab = QWidget()
        layout = QVBoxLayout()
        controls = QHBoxLayout()

        # Navigation buttons
        back_button = QPushButton("<")
        forward_button = QPushButton(">")

        # URL bar
        url_bar = QLineEdit()

        # Browser view
        browser = QWebEngineView()
        browser.setUrl(url)

        # Connect button actions
        back_button.clicked.connect(browser.back)
        forward_button.clicked.connect(browser.forward)
        url_bar.returnPressed.connect(lambda: browser.setUrl(QUrl(url_bar.text())))
        browser.urlChanged.connect(lambda qurl: url_bar.setText(qurl.toString()))

        # Add widgets to layouts
        controls.addWidget(back_button)
        controls.addWidget(forward_button)
        controls.addWidget(url_bar)

        layout.addLayout(controls)
        layout.addWidget(browser)
        tab.setLayout(layout)

        # Add the tab
        index = self.tabs.addTab(tab, label)
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def add_bookmark(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(1).widget()
        if isinstance(current_browser, QWebEngineView):
            current_url = current_browser.url().toString()
            self.bookmarked_urls.append(current_url)
            bookmark_action = QAction(current_url, self)
            bookmark_action.triggered.connect(lambda: self.add_new_tab(QUrl(current_url), current_url))
            self.bookmarks_menu.addAction(bookmark_action)


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
