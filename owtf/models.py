"""
owtf.db.models
~~~~~~~~~~~~~~

The SQLAlchemy models for every table in the OWTF DB.
"""
import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from owtf.config import db
from owtf.db.utils import model_repr


# This table actually allows us to make a many to many relationship
# between transactions table and grep_outputs table
target_association_table = db.Table(
    'target_session_association',
    db.Column('target_id', db.Integer, db.ForeignKey('targets.id')),
    db.Column('session_id', db.Integer, db.ForeignKey('sessions.id'))
)

db.Index('target_id_idx', target_association_table.c.target_id, postgresql_using='btree')


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    active = db.Column(db.Boolean, default=False)
    targets = db.relationship("Target", secondary=target_association_table, backref="sessions")


class Target(db.Model):
    __tablename__ = "targets"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    target_url = db.Column(db.String, unique=True)
    host_ip = db.Column(db.String)
    port_number = db.Column(db.String)
    url_scheme = db.Column(db.String)
    alternative_ips = db.Column(db.String, nullable=True)  # Comma seperated
    host_name = db.Column(db.String)
    host_path = db.Column(db.String)
    ip_url = db.Column(db.String)
    top_domain = db.Column(db.String)
    top_url = db.Column(db.String)
    scope = db.Column(db.Boolean, default=True)
    transactions = db.relationship("Transaction", cascade="delete")
    poutputs = db.relationship("PluginOutput", cascade="delete")
    urls = db.relationship("Url", cascade="delete")
    commands = db.relationship("Command", cascade="delete")
    # Also has a column session specified as backref in
    # session model
    works = db.relationship("Work", backref="target", cascade="delete")

    @hybrid_property
    def max_user_rank(self):
        user_ranks = [-1]
        user_ranks += [poutput.user_rank for poutput in self.poutputs]
        return(max(user_ranks))

    @hybrid_property
    def max_owtf_rank(self):
        owtf_ranks = [-1]
        owtf_ranks += [poutput.owtf_rank for poutput in self.poutputs]
        return(max(owtf_ranks))

    __repr__ = model_repr('target_url')


# This table actually allows us to make a many to many relationship
# between transactions table and grep_outputs table
transaction_association_table = db.Table(
    'transaction_grep_association',
    db.Column('transaction_id', db.Integer, db.ForeignKey('transactions.id')),
    db.Column('grep_output_id', db.Integer, db.ForeignKey('grep_outputs.id'))
)

db.Index('transaction_id_idx', transaction_association_table.c.transaction_id, postgresql_using='btree')


class Transaction(db.Model):
    __tablename__ = "transactions"

    target_id = db.Column(db.Integer, db.ForeignKey("targets.id"))
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    scope = db.Column(db.Boolean, default=False)
    method = db.Column(db.String)
    data = db.Column(db.String, nullable=True)  # Post DATA
    time = db.Column(db.Float(precision=10))
    time_human = db.Column(db.String)
    local_timestamp = db.Column(db.DateTime)
    raw_request = db.Column(db.Text)
    response_status = db.Column(db.String)
    response_headers = db.Column(db.Text)
    response_size = db.Column(db.Integer, nullable=True)
    response_body = db.Column(db.Text, nullable=True)
    binary_response = db.Column(db.Boolean, nullable=True)
    session_tokens = db.Column(db.String, nullable=True)
    login = db.Column(db.Boolean, nullable=True)
    logout = db.Column(db.Boolean, nullable=True)
    grep_outputs = db.relationship(
        "GrepOutput",
        secondary=transaction_association_table,
        cascade="delete",
        backref="transactions"
    )

    def __repr__(self):
        return "<HTTP Transaction (url='%s' method='%s' response_status='%s')>" % (self.url, self.method,
                                                                                   self.response_status)


class GrepOutput(db.Model):
    __tablename__ = "grep_outputs"

    target_id = db.Column(db.Integer, db.ForeignKey("targets.id"))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    output = db.Column(db.Text)
    # Also has a column transactions, which is added by
    # using backref in transaction

    __table_args__ = (db.UniqueConstraint('name', 'output', target_id),)


class Url(db.Model):
    __tablename__ = "urls"

    target_id = db.Column(db.Integer, db.ForeignKey("targets.id"))
    url = db.Column(db.String, primary_key=True)
    visited = db.Column(db.Boolean, default=False)
    scope = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return "<URL (url='%s')>" % (self.url)


class PluginOutput(db.Model):
    __tablename__ = "plugin_outputs"

    target_id = db.Column(db.Integer, db.ForeignKey("targets.id"))
    plugin_key = db.Column(db.String, db.ForeignKey("plugins.key"))
    # There is a column named plugin which is caused by backref from the plugin class
    id = db.Column(db.Integer, primary_key=True)
    plugin_code = db.Column(db.String)  # OWTF Code
    plugin_group = db.Column(db.String)
    plugin_type = db.Column(db.String)
    date_time = db.Column(db.DateTime, default=datetime.datetime.now())
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    output = db.Column(db.String, nullable=True)
    error = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=True)
    user_notes = db.Column(db.String, nullable=True)
    user_rank = db.Column(db.Integer, nullable=True, default=-1)
    owtf_rank = db.Column(db.Integer, nullable=True, default=-1)
    output_path = db.Column(db.String, nullable=True)

    @hybrid_property
    def run_time(self):
        return self.end_time - self.start_time

    __table_args__ = (db.UniqueConstraint('plugin_key', 'target_id'),)


class Command(db.Model):
    __tablename__ = "command_register"

    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    success = db.Column(db.Boolean, default=False)
    target_id = db.Column(db.Integer, db.ForeignKey("targets.id"))
    plugin_key = db.Column(db.String, db.ForeignKey("plugins.key"))
    modified_command = db.Column(db.String)
    original_command = db.Column(db.String, primary_key=True)

    @hybrid_property
    def run_time(self):
        return self.end_time - self.start_time


class Error(db.Model):
    __tablename__ = "errors"

    id = db.Column(db.Integer, primary_key=True)
    owtf_message = db.Column(db.String)
    traceback = db.Column(db.String, nullable=True)
    user_message = db.Column(db.String, nullable=True)
    reported = db.Column(db.Boolean, default=False)
    github_issue_url = db.Column(db.String, nullable=True)

    def __repr__(self):
        return "<Error (traceback='%s')>" % (self.traceback)


class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    dirty = db.Column(db.Boolean, default=False)  # Dirty if user edited it. Useful while updating
    resource_name = db.Column(db.String)
    resource_type = db.Column(db.String)
    resource = db.Column(db.String)
    __table_args__ = (db.UniqueConstraint('resource', 'resource_type', 'resource_name'),)


class ConfigSetting(db.Model):
    __tablename__ = "configuration"

    key = db.Column(db.String, primary_key=True)
    value = db.Column(db.String)
    section = db.Column(db.String)
    descrip = db.Column(db.String, nullable=True)
    dirty = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<ConfigSetting (key='%s', value='%s', dirty='%r')>" % (self.key, self.value, self.dirty)


class TestGroup(db.Model):
    __tablename__ = "test_groups"

    code = db.Column(db.String, primary_key=True)
    group = db.Column(db.String)  # web, network
    descrip = db.Column(db.String)
    hint = db.Column(db.String, nullable=True)
    url = db.Column(db.String)
    priority = db.Column(db.Integer)
    plugins = db.relationship("Plugin")


class Plugin(db.Model):
    __tablename__ = "plugins"

    key = db.Column(db.String, primary_key=True)  # key = type@code
    title = db.Column(db.String)
    name = db.Column(db.String)
    code = db.Column(db.String, db.ForeignKey("test_groups.code"))
    group = db.Column(db.String)
    type = db.Column(db.String)
    descrip = db.Column(db.String, nullable=True)
    file = db.Column(db.String)
    attr = db.Column(db.String, nullable=True)
    works = db.relationship("Work", backref="plugin", cascade="delete")
    outputs = db.relationship("PluginOutput", backref="plugin")

    def __repr__(self):
        return "<Plugin (code='%s', group='%s', type='%s')>" % (self.code, self.group, self.type)

    @hybrid_property
    def min_time(self):
        """
        Consider last 5 runs only, better performance and accuracy
        """
        poutputs_num = len(self.outputs)
        if poutputs_num != 0:
            if poutputs_num < 5:
                run_times = [poutput.run_time for poutput in self.outputs]
            else:
                run_times = [poutput.run_time for poutput in self.outputs[-5:]]
            return min(run_times)
        else:
            return None

    @hybrid_property
    def max_time(self):
        """
        Consider last 5 runs only, better performance and accuracy
        """
        poutputs_num = len(self.outputs)
        if poutputs_num != 0:
            if poutputs_num < 5:
                run_times = [poutput.run_time for poutput in self.outputs]
            else:
                run_times = [poutput.run_time for poutput in self.outputs[-5:]]
            return max(run_times)
        else:
            return None

    __table_args__ = (db.UniqueConstraint('type', 'code'),)


class Work(db.Model):
    __tablename__ = "worklist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    target_id = db.Column(db.Integer, db.ForeignKey("targets.id"))
    plugin_key = db.Column(db.String, db.ForeignKey("plugins.key"))
    active = db.Column(db.Boolean, default=True)
    # Columns plugin and target are created using backrefs

    __table_args__ = (db.UniqueConstraint('target_id', 'plugin_key'),)

    def __repr__(self):
        return "<Work (target='%s', plugin='%s')>" % (self.target_id, self.plugin_key)


class Mapping(db.Model):
    __tablename__ = 'mappings'

    owtf_code = db.Column(db.String, primary_key=True)
    mappings = db.Column(db.String)
    category = db.Column(db.String, nullable=True)
