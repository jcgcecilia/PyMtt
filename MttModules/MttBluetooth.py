import time, bluetooth
import sys

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget


def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug


class Worker(QObject):
    """
    Must derive from QObject in order to emit signals, connect slots to other signals, and operate in a QThread.
    """

    sig_done = pyqtSignal()  # worker id: emitted at end of work()
    sig_msg = pyqtSignal(str)  # message to be shown to user
    
    def __init__(self):
        super().__init__()

    @pyqtSlot()
    def work(self):
        self.sig_msg.emit("Start discovering devices")
        nearby_devices = bluetooth.discover_devices(lookup_names= True)
        for device in nearby_devices:
            self.sig_msg.emit(str(device))
        
        self.sig_done.emit()

class MyWidget(QWidget):
    NUM_THREADS = 5

    sig_start = pyqtSignal()  # needed only due to PyCharm debugger bug (!)
    sig_abort_workers = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thread Example")
        form_layout = QVBoxLayout()
        self.setLayout(form_layout)
        self.resize(400, 800)

        self.button_start_threads = QPushButton()
        self.button_start_threads.clicked.connect(self.start_threads)
        self.button_start_threads.setText("Start thread")
        form_layout.addWidget(self.button_start_threads)

        self.log = QTextEdit()
        form_layout.addWidget(self.log)

        QThread.currentThread().setObjectName('main')  # threads can be named, useful for log output
        self.__workers_done = None
        self.__threads = None

    def start_threads(self):
        self.log.append('Starting thread')
        self.button_start_threads.setDisabled(True)
#         self.button_stop_threads.setEnabled(True)

        self.worker = Worker()
        self.thread = QThread()
        self.thread.setObjectName('thread_')
#         self.__threads.append((thread, worker))  # need to store worker too otherwise will be gc'd
        self.worker.moveToThread(self.thread)

        # get progress messages from worker:
        self.worker.sig_done.connect(self.on_worker_done)
        self.worker.sig_msg.connect(self.log.append)
#         thread.started.connect(worker.work)
        # control worker:
        # get read to start worker:
        self.sig_start.connect(self.worker.work)  # needed due to PyCharm debugger bug (!); comment out next line
        self.thread.start()  # this will emit 'started' and start thread's event loop

        self.sig_start.emit()  # needed due to PyCharm debugger bug (!)'''
        
    @pyqtSlot()
    def on_worker_done(self):
        self.log.append("Work done")


if __name__ == "__main__":
    app = QApplication([])

    form = MyWidget()
    form.show()

    sys.exit(app.exec_())

# 
# 
# 
# import bluetooth, sys
# 
# from PyQt5.Qt import QObject, QApplication
# from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
# 
# class Worker(QObject):
#     
#     sig_done = pyqtSignal()
# 
#     def __init__(self):
#         super().__init__()
# 
#     @pyqtSlot()
#     def do_work(self):
#         print("Starting work")
#         nearby_devices = bluetooth.discover_devices(lookup_names= True)
#         print(nearby_devices.__class__)
#         self.sig_done.emit(nearby_devices)
# 
# 
# class MttBluetooth(QObject):
#     '''
#     classdocs
#     '''
#     sig_start = pyqtSignal()
# 
#     def __init__(self):
#         super().__init__()
#         
#     def get_devices(self):
#         print("Starting thread")
#         self.__workers_done = 0
#         worker = Worker()
#         thread = QThread()
#         worker.moveToThread(thread)
# 
#         # get progress messages from worker:
#         worker.sig_done.connect(self.on_worker_done)
# 
#         thread.started.connect(worker.do_work)  # needed due to PyCharm debugger bug (!); comment out next line
# #         thread.started.connect(worker.work)
#         thread.start()  # this will emit 'started' and start thread's event loop
# #         self.sig_start.emit()  # needed due to PyCharm debugger bug (!
# #         thread.wait()
# 
#     @pyqtSlot()
#     def on_worker_done(self):
#         print("Work done")
# 
# if __name__ == "__main__":
#     app = QApplication([])
#     handler = MttBluetooth()
#     handler.get_devices()
# #     handler.join()
#     
#     print("Stop here")
#     sys.exit(app.exec_())