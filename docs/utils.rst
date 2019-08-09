=================
Utility / Helpers
=================


parse_table_qualified_name()
----------------------------
`atlasclient` provides helper function to parse the table qualified name and returns a dictionary
containing `db_name`, `table_name` and `cluster_name` as keys::

    from atlasclient.utils import parse_table_qualified_name

    # Happy Scenario
    qualified_name = 'database.table@cluster'
    qn_dict = parse_table_qualified_name(qualified_name)
    print(qn_dict["db_name"])
    # Output: database

    print(qn_dict["table_name"])
    # Output: table

    print(qn_dict["cluster_name"])
    # Output: cluster


In case if the entity is created manually and somehow does not fully satisfies the atlas qualified name
pattern, this helper function handles the edge cases::

    qualified_name = 'table@cluster'
    qn_dict = parse_table_qualified_name(qualified_name)
    print(qn_dict["db_name"])
    # Output: default

    print(qn_dict["table_name"])
    # Output: table

    print(qn_dict["cluster_name"])
    # Output: cluster

make_table_qualified_name()
----------------------------
There is also a function to make the table qualified name, back from the parsed result.
It verifies if all three i.e., `table_name`, `cluster` and `db` parameters are there and not `default`.
If the value is default or not available, then this helper handles the edge case accordingly::

    from atlasclient.utils import make_table_qualified_name

    # Happy Scenario
    qualified_name = make_table_qualified_name('table', 'cluster', 'database')
    print(qualified_name)
    # Output: 'database.table@cluster'
