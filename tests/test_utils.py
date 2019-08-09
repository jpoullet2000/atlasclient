from atlasclient.utils import (parse_table_qualified_name, make_table_qualified_name,
                               DEFAULT_DB_CLUSTER)

DB = 'database_name'
CL = 'cluster_name'
TB = 'table_name'


class TestUtils():
    def test_parse_table_qn(self):
        qualified_name = f'{DB}.{TB}@{CL}'
        qn_dict = parse_table_qualified_name(qualified_name)
        assert qn_dict['db_name'] == DB
        assert qn_dict['cluster_name'] == CL
        assert qn_dict['table_name'] == TB

    def test_parse_table_qn_without_db(self):
        qualified_name = f'{TB}@{CL}'
        qn_dict = parse_table_qualified_name(qualified_name)
        assert qn_dict['db_name'] == DEFAULT_DB_CLUSTER
        assert qn_dict['cluster_name'] == CL
        assert qn_dict['table_name'] == TB

    def test_parse_table_qn_without_cluster(self):
        qualified_name = f'{DB}.{TB}'
        qn_dict = parse_table_qualified_name(qualified_name)
        assert qn_dict['db_name'] == DB
        assert qn_dict['cluster_name'] == DEFAULT_DB_CLUSTER
        assert qn_dict['table_name'] == TB

    def test_parse_table_qn_only_table(self):
        qualified_name = f'{TB}'
        qn_dict = parse_table_qualified_name(qualified_name)
        assert qn_dict['db_name'] == DEFAULT_DB_CLUSTER
        assert qn_dict['cluster_name'] == DEFAULT_DB_CLUSTER
        assert qn_dict['table_name'] == TB

    def test_make_table_qn(self):
        qn = make_table_qualified_name(TB, CL, DB)
        assert qn == f'{DB}.{TB}@{CL}'

    def test_make_table_qn_with_default_database(self):
        qn = make_table_qualified_name(TB, CL, DEFAULT_DB_CLUSTER)
        assert qn == f'{TB}@{CL}'

    def test_make_table_qn_with_default_cluster(self):
        qn = make_table_qualified_name(TB, DEFAULT_DB_CLUSTER, DB)
        assert qn == f'{DB}.{TB}'

    def test_make_table_qn_only_table_with_default_db_cluster(self):
        qn = make_table_qualified_name(TB, DEFAULT_DB_CLUSTER, DEFAULT_DB_CLUSTER)
        assert qn == f'{TB}'

    def test_make_table_qn_without_database(self):
        qn = make_table_qualified_name(TB, CL)
        assert qn == f'{TB}@{CL}'

    def test_make_table_qn_without_cluster(self):
        qn = make_table_qualified_name(TB, db=DB)
        assert qn == f'{DB}.{TB}'

    def test_make_table_qn_only_table(self):
        qn = make_table_qualified_name(TB)
        assert qn == f'{TB}'
