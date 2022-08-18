import ast
import json
import logging
import re

logger = logging.getLogger(__name__)


def str2obj(var):
    """
    Convert string dict/array to an actual dict/array
    this function is used to convert trackdb_configuration
    and trackdb_data from string (as stored in MySQL) to JSON
    (as it need for it to be stored in Elasticsearch when enriching the document)
    :returns: JSON object
    """
    if isinstance(var, dict) or isinstance(var, list):
        return var

    try:
        var = ast.literal_eval(var)
    # if the result of ast.literal_eval is not a dict or array
    # print the error and return None
    except ValueError as ex:
        logger.error(ex)
        return None

    # Take into account values that are not lists/dicts of strings
    # and don't cause ValueErrors, for example ast.literal_eval("'a'") evaluates to 'a',
    # and ast.literal_eval("1") evaluates to 1
    if not (isinstance(var, list) or isinstance(var, dict)):
        return None

    string_var_double_quote = json.dumps(var)
    return json.loads(string_var_double_quote)


def escape_ansi(line):
    """
    Remove the ANSI escape sequences from a string
    https://stackoverflow.com/q/14693701/4488332
    """
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)
    

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)
