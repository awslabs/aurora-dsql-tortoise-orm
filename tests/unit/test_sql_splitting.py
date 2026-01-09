# # Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# # SPDX-License-Identifier: Apache-2.0

from aurora_dsql_tortoise.common.config import split_sql


def test_basic_splitting():
    result = split_sql("CREATE TABLE a (id INT); CREATE TABLE b (id INT)")
    assert result == ["CREATE TABLE a (id INT)", "CREATE TABLE b (id INT)"]


def test_semicolon_in_single_quoted_string():
    result = split_sql("INSERT INTO t VALUES ('a;b'); INSERT INTO t VALUES ('c')")
    assert result == ["INSERT INTO t VALUES ('a;b')", "INSERT INTO t VALUES ('c')"]


def test_semicolon_in_double_quoted_identifier():
    result = split_sql('CREATE TABLE "my;table" (id INT); CREATE TABLE other (id INT)')
    assert result == ['CREATE TABLE "my;table" (id INT)', "CREATE TABLE other (id INT)"]


def test_escaped_single_quote():
    result = split_sql("INSERT INTO t VALUES ('it''s;here'); SELECT 1")
    assert result == ["INSERT INTO t VALUES ('it''s;here')", "SELECT 1"]


def test_escaped_double_quote():
    result = split_sql('CREATE TABLE "has""semi;colon" (id INT); SELECT 1')
    assert result == ['CREATE TABLE "has""semi;colon" (id INT)', "SELECT 1"]


def test_mixed_quotes():
    result = split_sql("""INSERT INTO t VALUES ('he said "hi;there"'); SELECT 1""")
    assert result == ["""INSERT INTO t VALUES ('he said "hi;there"')""", "SELECT 1"]


def test_trailing_semicolon():
    result = split_sql("SELECT 1;")
    assert result == ["SELECT 1"]


def test_no_semicolon():
    result = split_sql("SELECT 1")
    assert result == ["SELECT 1"]


def test_empty_input():
    result = split_sql("")
    assert result == []


def test_only_whitespace():
    result = split_sql("   ")
    assert result == []


def test_multiple_consecutive_semicolons():
    result = split_sql("SELECT 1;; SELECT 2")
    assert result == ["SELECT 1", "SELECT 2"]


def test_dollar_quoted_string():
    result = split_sql("SELECT $$contains;semicolon$$; SELECT 1")
    assert result == ["SELECT $$contains;semicolon$$", "SELECT 1"]


def test_tagged_dollar_quoted_string():
    result = split_sql("SELECT $foo$contains;semicolon$foo$; SELECT 1")
    assert result == ["SELECT $foo$contains;semicolon$foo$", "SELECT 1"]


def test_single_quote_inside_dollar_quoted_string():
    result = split_sql("SELECT $$it's fine$$; SELECT 1")
    assert result == ["SELECT $$it's fine$$", "SELECT 1"]


def test_quoted_string_before_and_inside_dollar_quoted_string():
    result = split_sql("SELECT 'a', $$it's; fine$$; SELECT 1")
    assert result == ["SELECT 'a', $$it's; fine$$", "SELECT 1"]


def test_double_quote_inside_dollar_quoted_string():
    result = split_sql('SELECT $$say "hello; world"$$; SELECT 1')
    assert result == ['SELECT $$say "hello; world"$$', "SELECT 1"]


def test_combined_stress_test():
    sql = """
          CREATE TABLE "weird;name" (id INT);
          INSERT INTO t VALUES ('it''s;tricky');
          CREATE TABLE "a""b;c" (x INT); SELECT 1"""
    result = split_sql(sql)
    assert result == [
        'CREATE TABLE "weird;name" (id INT)',
        "INSERT INTO t VALUES ('it''s;tricky')",
        'CREATE TABLE "a""b;c" (x INT)',
        "SELECT 1",
    ]
