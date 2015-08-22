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

    view = Viewer(params.filename)
    return app.exec_()


def parse_args(params=sys.argv[1:]):
    parser = ArgumentParser(description="A long long time ago...")
    parser.add_argument("filename", nargs="?", default="demo.rst",
                        help="reStructuredText file")
    parser.add_argument("--interval", "-i", type=int, default=250,
                        help="Milliseconds between checking the file")

    return parser.parse_args(params)


class Viewer(QtGui.QWidget):
    TITLE = "RST Watcher"

    FILE_FMT = '<span style="color: #11c031; font-weight: bold">{}</span>'

    def __init__(self, filename, *args, **kwargs):
        super(Viewer, self).__init__(*args, **kwargs)
        self.monitor = FileMonitor(filename)
        self.toolbar = QtGui.QToolBar(self)
        self.webview = QtWebKit.QWebView(self)
        self._filename_label = QtGui.QLabel("")

        # Bind the monitor to reload the file.
        self.monitor.changed.connect(self._load_file)

        self.setWindowTitle(self.TITLE)
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self.webview.show()
        vbox.addWidget(self.toolbar)

        vbox.addWidget(self.webview)

        self._setup_toolbar()
        self._load_file()
        self.toolbar.show()
        self.webview.show()
        self.show()

    def _setup_toolbar(self):
        """
        Put actions in the toolbar.
        """
        self.toolbar.addAction("Open", self._open_file)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self._filename_label)

    def _load_file(self):
        """
        Load the file currently being monitored.
        """
        if not self.monitor.filename:
            self._filename_label.setText("")
            self.webview.setHtml("")
        else:
            self.monitor.mark_current()
            self._filename_label.setText(
                self.FILE_FMT.format(os.path.split(self.monitor.filename)[1])
            )
            self._filename_label.repaint()
            with open(self.monitor.filename) as src:
                self.webview.setHtml(publish_string(src.read(),
                                                    writer_name="html"))

    def _open_file(self):
        """
        Show the open file dialog.
        """
        self.monitor.filename = QtGui.QFileDialog.getOpenFileName()[0]
        self._load_file()


class FileMonitor(QtCore.QObject):
    """
    Emits a signal when a file is modified.
    """
    changed = QtCore.Signal()

    def __init__(self, filename, interval=250, *args, **kwargs):
        super(FileMonitor, self).__init__(*args, **kwargs)
        self._prev_mtime = None
        self._filename = None
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.check)
        self.filename = filename

    @property
    def filename(self):
        """
        Get the current filename.
        """
        return self._filename

    @filename.setter
    def filename(self, value):
        """
        Set the filename. If value is None then the time will be stopped.
        """
        self.timer.stop()
        if value:
            self._filename = value
            self.mark_current()
            self.timer.start()

    @property
    def current_mtime(self):
        return os.stat(self._filename).st_mtime

    def mark_current(self):
        """
        Updates the saved modified time to the current modified time.
        """
        self._prev_mtime = self.current_mtime

    def check(self):
        """
        Check if the file has been modified, if it has than emits
        a changed signal.
        """
        if self._prev_mtime < self.current_mtime:
            self.changed.emit()


if __name__ == "__main__":
    sys.exit(main(parse_args()))
