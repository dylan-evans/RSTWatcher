"""
A small program for viewing a rendered reStructuredText file which updates
when the file is modified.
"""
import os
import sys
from argparse import ArgumentParser

from docutils.core import publish_string
from PySide import QtCore, QtWebKit, QtGui


def main(params):
    """
    Run the program.
    :param params: A namespace returned from parse_args.
    """
    app = QtGui.QApplication(sys.argv)

    win = QtGui.QMainWindow()
    win.setWindowTitle("RST Viewer")

    widgydidge = QtGui.QWidget()
    vbox = QtGui.QVBoxLayout()
    widgydidge.setLayout(vbox)
    win.setCentralWidget(widgydidge)

    monitor = SourceMonitor(params.filename, QtWebKit.QWebView())
    monitor.start()
    vbox.addWidget(monitor._webview)

    tools = QtGui.QToolBar()
    tools.show()
    tools.addAction("Open", monitor.open_file)
    vbox.addWidget(tools)
    # TODO: Add button for opening a file.
    # TODO: Add status widget (assuming the toolbar allows that)

    win.show()
    return app.exec_()


def parse_args(params=sys.argv[1:]):
    parser = ArgumentParser(description="A long long time ago...")
    parser.add_argument("filename", nargs="?", default="demo.rst",
                        help="reStructuredText file")
    parser.add_argument("--interval", "-i", type=int, default=200,
                        help="Milliseconds between checking the file")

    return parser.parse_args(params)


class SourceMonitor(object):
    """
    Monitor an rst source file and load it into the web view.
    """
    def __init__(self, filename, webview, interval=200):
        self._filename = filename
        self._webview = webview
        self._cur_mtime = None
        self._timer = None
        self._interval = interval
        self.load()

        # Setup the timer, it still needs to be started.
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(False)
        self._timer.setInterval(self._interval)
        self._timer.timeout.connect(self.reload_if_modified)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, name):
        # TODO: Check if the file exists and display an error if it doesn't
        if not name:
            self._webview.setHtml("")
        self._filename = name
        # TODO: Show the filename in the toolbar.
        self.load()

    def load(self):
        """
        Read the file, process it with docutils and update the web view.
        """
        with open(self._filename) as src:
            self._webview.setHtml(publish_string(src.read(), writer_name="html"))
        self._cur_mtime = os.stat(self._filename).st_mtime
        self._webview.show()

    def modified(self):
        """
        Check if the file has been modified since it was last read.
        :return: True or False.
        """
        print self.filename
        mtime = os.stat(self._filename).st_mtime
        return not self._cur_mtime or self._cur_mtime < mtime

    def reload_if_modified(self):
        """
        Refresh the web view if the file has been modified.
        """
        if self.modified():
            self.load()

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()


    def open_file(self):
        self.filename = QtGui.QFileDialog.getOpenFileName()[0]


if __name__ == "__main__":
    sys.exit(main(parse_args()))
