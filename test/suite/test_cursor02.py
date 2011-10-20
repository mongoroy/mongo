#!/usr/bin/env python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2008-2011 WiredTiger, Inc.
#	All rights reserved.
#
# test_cursor02.py
# 	Cursor operations on small tables.
#

import unittest
import wiredtiger
from test_cursor_tracker import TestCursorTracker

class test_cursor02(TestCursorTracker):
    """
    Cursor operations on small tables of each access method.
    We use the TestCursorTracker base class to generate
    key/value content and to track/verify content
    after inserts and removes.
    """
    scenarios = [
        ('row', dict(tablekind='row')),
        ('col', dict(tablekind='col')),
        #('fix', dict(tablekind='fix'))
        ]

    def create_session_and_cursor(self, ninitialentries):
        tablearg = "table:" + self.table_name1
        if self.tablekind == 'row':
            keyformat = 'key_format=S'
        else:
            keyformat = 'key_format=r'  # record format
        if self.tablekind == 'fix':
            valformat = 'value_format=8t'
        else:
            valformat = 'value_format=S'
        create_args = keyformat + ',' + valformat + self.config_string()
        self.session_create(tablearg, create_args)
        self.pr('creating cursor')
        self.cur_initial_conditions(self.table_name1, ninitialentries, self.tablekind, None, None)
        return self.session.open_cursor(tablearg, None, 'append')

    def test_multiple_remove(self):
        """
        Test multiple deletes at the same place
        """
        cursor = self.create_session_and_cursor(10)
        self.cur_first(cursor)
        self.cur_check_forward(cursor, 5)

        self.cur_remove_here(cursor)
        self.cur_next(cursor)
        self.cur_check_here(cursor)

        self.cur_remove_here(cursor)
        self.cur_next(cursor)
        self.cur_check_here(cursor)
        self.cur_check_forward(cursor, 2)

        #self.cur_dump_here(cursor, 'after second next: ')
        cursor.close(None)

    def test_insert_and_remove(self):
        """
        Test a variety of insert, deletes and iteration
        """
        cursor = self.create_session_and_cursor(10)
        #self.table_dump(self.table_name1)
        self.cur_insert(cursor, 2, 5)
        self.cur_insert(cursor, 2, 6)
        self.cur_insert(cursor, 2, 4)
        self.cur_insert(cursor, 2, 7)
        self.cur_first(cursor)
        self.cur_check_forward(cursor, 5)
        self.cur_remove_here(cursor)
        self.cur_check_forward(cursor, 5)
        self.cur_remove_here(cursor)
        self.cur_check_forward(cursor, 1)
        self.cur_remove_here(cursor)
        self.cur_check_forward(cursor, 2)
        self.cur_check_backward(cursor, 4)
        self.cur_remove_here(cursor)
        self.cur_check_backward(cursor, 2)
        self.cur_check_forward(cursor, 5)
        self.cur_check_backward(cursor, -1)
        self.cur_check_forward(cursor, -1)
        self.cur_last(cursor)
        self.cur_check_backward(cursor, -1)
        cursor.close(None)

    def test_iterate_empty(self):
        """
        Test iterating an empty table
        """
        cursor = self.create_session_and_cursor(0)
        self.cur_first(cursor, wiredtiger.WT_NOTFOUND)
        self.cur_check_forward(cursor, -1)
        self.cur_check_backward(cursor, -1)
        self.cur_last(cursor, wiredtiger.WT_NOTFOUND)
        self.cur_check_backward(cursor, -1)
        self.cur_check_forward(cursor, -1)
        cursor.close(None)

    def test_iterate_one_preexisting(self):
        """
        Test iterating a table that contains one preexisting entry
        """
        cursor = self.create_session_and_cursor(1)
        self.cur_first(cursor)
        self.cur_check_forward(cursor, -1)
        self.cur_check_backward(cursor, -1)
        self.cur_last(cursor)
        self.cur_check_backward(cursor, -1)
        self.cur_check_forward(cursor, -1)
        cursor.close(None)

    def test_iterate_one_added(self):
        """
        Test iterating a table that contains one newly added entry
        """
        cursor = self.create_session_and_cursor(0)
        self.cur_insert(cursor, 1, 0)
        self.cur_check_forward(cursor, -1)
        self.cur_first(cursor)
        self.cur_check_forward(cursor, -1)
        self.cur_check_backward(cursor, -1)
        self.cur_last(cursor)
        self.cur_check_backward(cursor, -1)
        self.cur_check_forward(cursor, -1)
        cursor.close(None)


if __name__ == '__main__':
    wttest.run()
