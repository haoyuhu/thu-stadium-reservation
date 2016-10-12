import win32service
import win32serviceutil
import win32event
from config.Config import Config
from plugins.BookScheduler import BookScheduler


class BackendService(win32serviceutil.ServiceFramework):
    # you can NET START/STOP the service by the following name
    _svc_name_ = "thu-stadium-reservation"
    # this text shows up as the service name in the Service
    # Control Manager (SCM)
    _svc_display_name_ = "Stadium Reservation Service"
    # this text shows up as the description in the SCM
    _svc_description_ = "Make stadium reservation in Tsinghua automatically"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # create an event to listen for stop requests on
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = Config().get_logger()
        self.scheduler = BookScheduler()
        self.scheduler.init()

    # core logic of the service
    def SvcDoRun(self):
        self.start()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    # called when we're being shut down
    def SvcStop(self):
        # tell the SCM we're shutting down
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # fire the stop event
        win32event.SetEvent(self.hWaitStop)
        self.stop()

    def start(self):
        self.scheduler.run()
        self.logger.log('thu-stadium-reservation service started!')

    def stop(self):
        self.scheduler.stop()
        self.logger.log('thu-stadium-reservation service stop...')
