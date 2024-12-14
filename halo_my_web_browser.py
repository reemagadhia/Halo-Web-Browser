from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtGui
import requests
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Halo Web Browser")
        self.setWindowIcon(QtGui.QIcon('halo.webp'))

        # Google Safe Browsing API key
        self.api_key = "API_KEY" #Cannot include our API-Key in the code due to Github restrictions 

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

        # Update the URL bar when the browser URL changes
        browser.urlChanged.connect(lambda qurl: self.handle_url_change(qurl, browser, url_bar))

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

        # Set the URL bar to the initial URL
        url_bar.setText(url.toString())

    def handle_url_change(self, qurl, browser, url_bar):
        url = qurl.toString()
        url_bar.setText(url)

        # Check URL safety
        if self.is_url_unsafe(url):
            QMessageBox.warning(self, "Security Alert", f"The URL you are trying to access may be unsafe:\n{url}")
            # browser.setUrl(QUrl("https://www.google.com"))  # Redirect to a safe page

    def is_url_unsafe(self, url):
        api_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
        headers = {"Content-Type": "application/json"}
        payload = {
            "client": {
                "clientId": "halo-browser",
                "clientVersion": "1.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [
                    {"url": url}
                ]
            }
        }

        response = requests.post(api_url, headers=headers, json=payload, params={"key": self.api_key})
        if response.status_code == 200:
            result = response.json()
            return "matches" in result and len(result["matches"]) > 0
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return False

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def add_bookmark(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(1).widget()
        if isinstance(current_browser, QWebEngineView):
            current_url = current_browser.url().toString()
            self.bookmarked_urls.append(current_url)
            bookmark_action = QAction(current_url, self)
            bookmark_action.triggered.connect(lambda: self.add_new_tab(QUrl(current_url), "New Tab"))
            self.bookmarks_menu.addAction(bookmark_action)

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
