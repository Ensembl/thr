"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import pytest
from trackhubs.utils import str2obj, escape_ansi, remove_html_tags


@pytest.mark.parametrize(
    'the_string, expected_output, expected_type',
    [
        ("{}", {}, dict),
        ("{'a': 'b'}", {'a': 'b'}, dict),
        ("{'a': {'b': [11, 12]}}", {'a': {'b': [11, 12]}}, dict),
        ("{1: 1, 2: 4}", {'1': 1, '2': 4}, dict),
        ("[]", [], list),
        ("['a', 11, True]", ['a', 11, True], list),
        ("['a', [11, True], 44]", ['a', [11, True], 44], list),
        ("foo", None, type(None)),
        (1, None, type(None)),
        (None, None, type(None)),
        ({}, {}, dict),
        ({'a': {'b': [11, 12]}}, {'a': {'b': [11, 12]}}, dict),
        ([], [], list),
        (['a', [11, True], 44], ['a', [11, True], 44], list),
        ("'a'", None, type(None)),
        ("'1'", None, type(None)),
    ]
)
def test_str2obj(the_string, expected_output, expected_type):
    actual_output = str2obj(the_string)
    assert actual_output == expected_output
    assert isinstance(actual_output, expected_type)


@pytest.mark.parametrize(
    'string_line, expected_result',
    [
        ('\x1b[32;1mAll TrackDB are updated successfully!\x1b[0m\n', 'All TrackDB are updated successfully!\n'),
        ('\t\x1b[00m\x1b[01;31manother_example\x1b[00m\x1b[01;31m', '\tanother_example'),
    ]
)
def test_escape_ansi(string_line, expected_result):
    actual_result = escape_ansi(string_line)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'html_text, expected_result',
    [
        ("<h1 class='foo'>Lorem ipsum</h1>", "Lorem ipsum"),
        ("<h1 class='foo'>Lorem ipsum</h1> dolor sit amet", "Lorem ipsum dolor sit amet"),
        ("Lorem ipsum</h1>", "Lorem ipsum"),
        ("<h1 class='foo'>Lorem ipsum", "Lorem ipsum"),
        ("Lorem ipsum", "Lorem ipsum"),
        ("<br/>", ""),
    ]
)
def test_remove_html_tags(html_text, expected_result):
    actual_result = remove_html_tags(html_text)
    assert actual_result == expected_result
