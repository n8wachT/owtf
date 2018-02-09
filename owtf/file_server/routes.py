import tornado.web

from owtf.file_server.handlers import StaticFileHandler
from owtf.utils.file import get_output_dir_target, get_dir_worker_logs


HANDLERS = [
    tornado.web.url(r'/logs/(.*)', StaticFileHandler, {'path': get_dir_worker_logs()}, name="logs_files_url"),
    tornado.web.url(r'/(.*)', StaticFileHandler, {'path': get_output_dir_target()}, name="output_files_url"),
]
