from flask.cli import FlaskGroup

description = "OWASP OWTF, the Offensive (Web) Testing Framework, is an OWASP+PTES-focused try " + \
    "to unite great tools and make pentesting more efficient @owtfp http://owtf.org"

cli = FlaskGroup(help=description)
