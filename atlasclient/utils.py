#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import re
import base64

try:
    from logging import NullHandler  # pylint: disable=unused-import
except ImportError:
    from logging import Handler


    class NullHandler(Handler):
        def emit(self, record):
            pass

DEFAULT_PORTS = {
    'http': 80,
    'https': 443,
}

DEFAULT_TABLE_QN_REGEX = re.compile(r"""
    ^(?P<db_name>.*?)\.(?P<table_name>.*)@(?P<cluster_name>.*?)$
    """, re.X)

DEFAULT_DB_CLUSTER = 'default'


def normalize_underscore_case(name):
    """Normalize an underscore-separated descriptor to something more readable.

    i.e. 'NAGIOS_SERVER' becomes 'Nagios Server', and 'host_components' becomes
    'Host Components'
    """
    normalized = name.lower()
    normalized = re.sub(r'_(\w)',
                        lambda match: ' ' + match.group(1).upper(),
                        normalized)
    return normalized[0].upper() + normalized[1:]


def normalize_camel_case(name):
    """Normalize a camelCase descriptor to something more readable.

    i.e. 'camelCase' or 'CamelCase' becomes 'Camel Case'
    """
    normalized = re.sub('([a-z])([A-Z])',
                        lambda match: ' '.join([match.group(1), match.group(2)]),
                        name)
    return normalized[0].upper() + normalized[1:]


def version_tuple(version):
    """Convert a version string or tuple to a tuple.

    Should be returned in the form: (major, minor, release).
    """
    if isinstance(version, str):
        return tuple(int(x) for x in version.split('.'))
    elif isinstance(version, tuple):
        return version
    else:
        raise ValueError("Invalid version: %s" % version)


def version_str(version):
    """Convert a version tuple or string to a string.

    Should be returned in the form: major.minor.release
    """
    if isinstance(version, str):
        return version
    elif isinstance(version, tuple):
        return '.'.join([str(int(x)) for x in version])
    else:
        raise ValueError("Invalid version: %s" % version)


def generate_http_basic_token(username, password):
    """
    Generates a HTTP basic token from username and password

    Returns a token string (not a byte)
    """
    token = base64.b64encode('{}:{}'.format(username, password).encode('utf-8')).decode('utf-8')
    return token


def generate_base_url(host, protocol=None, port=None):
    matches = re.match(r'^(([^:]+)://)?([^/:]+)(:([^/]+))?', host)
    (_, derived_proto, derived_host, _, derived_port) = matches.groups()
    if derived_proto is None:
        derived_proto = protocol or 'http'
    if derived_proto not in DEFAULT_PORTS:
        raise ValueError()

    if derived_port is None:
        derived_port = port or DEFAULT_PORTS[derived_proto]

    derived_port = int(derived_port)

    url_params = {
        'protocol': derived_proto,
        'host': derived_host,
        'port': str(derived_port),
    }
    return "{protocol}://{host}:{port}".format(**url_params)


def parse_table_qualified_name(qualified_name, qn_regex=DEFAULT_TABLE_QN_REGEX):
    """
    Parses the Atlas' table qualified name
    :param qualified_name: Qualified Name of the table
    :return: A dictionary consisting of database name,
    table name and cluster name of the table.
    If database or cluster name not found,
    then uses the 'atlas_default' as both of them.
    """
    def apply_qn_regex(name, table_qn_regex):
        return table_qn_regex.match(name)

    _regex_result = apply_qn_regex(qualified_name, qn_regex)

    if not _regex_result:
        qn_regex = re.compile(r"""
        ^(?P<table_name>.*)@(?P<cluster_name>.*?)$
        """, re.X)
        _regex_result = apply_qn_regex(qualified_name, qn_regex)

    if not _regex_result:
        qn_regex = re.compile(r"""
        ^(?P<db_name>.*?)\.(?P<table_name>.*)$
        """, re.X)
        _regex_result = apply_qn_regex(qualified_name, qn_regex)

    if not _regex_result:
        qn_regex = re.compile(r"""
        ^(?P<table_name>.*)$
        """, re.X)
        _regex_result = apply_qn_regex(qualified_name, qn_regex)

    _regex_result = _regex_result.groupdict()

    qn_dict = {
        'table_name': _regex_result.get('table_name', qualified_name),
        'db_name': _regex_result.get('db_name', DEFAULT_DB_CLUSTER),
        'cluster_name': _regex_result.get('cluster_name', DEFAULT_DB_CLUSTER),
    }

    return qn_dict


def make_table_qualified_name(table_name, cluster=None, db=None):
    """
    Based on the given parameters, generate the Atlas' table qualified Name
    :param db: Database Name of the table
    :param table_name: Table Name
    :param cluster: Cluster Name of the table
    :return: A string i.e., Qualified Name of the table
    If database or cluster name are 'atlas_default', then simply strips that part.
    """
    qualified_name = table_name
    if db and db != DEFAULT_DB_CLUSTER:
        qualified_name = '{}.{}'.format(db, qualified_name)

    if cluster and cluster != DEFAULT_DB_CLUSTER:
        qualified_name = '{}@{}'.format(qualified_name, cluster)

    return qualified_name
