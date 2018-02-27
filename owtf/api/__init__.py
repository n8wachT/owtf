from flask_restful import Resource, Api

from owtf.api.config import Configuration
from owtf.api.plugin import PluginData, PluginOutput, PluginNameOutput
from owtf.api.report import ReportExport
from owtf.api.session import OWTFSession
from owtf.api.targets import TargetConfig, TargetConfigSearch
from owtf.api.transactions import TransactionData, TransactionHrt, TransactionSearch
from owtf.api.work import Worker, Worklist, WorklistSearch


class APICatchall(Resource):
    def get(self, path):
        return {'error': 'Not Found'}, 404

    post = get
    put = get
    delete = get
    patch = get


