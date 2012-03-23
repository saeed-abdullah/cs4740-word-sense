import unittest2
from mock import MagicMock, patch
import mock
from StringIO import StringIO

from .. import datautil

class DataUtilTest(unittest2.TestCase):

    def setUp(self):
        pass

    def test_get_data_line(self):
        lines = """1

        %23
        2
        3%
        """

        filename=""
        m = mock_open(data=StringIO(lines))
        open_name = "{0}.open".format(datautil.__name__)

        with patch(open_name, m, create=True):
            for line in datautil.get_data_line(filename, comment='%'):
                self.assertGreater(len(line), 0)
                self.assertFalse(line.startswith('%'))

    def test_write_arff_header(self):
        m = mock_open()

        # The output should look like:
        # % Comment
        # @RELATION wsd
        # @ATTRIBUTE f1 NUMERIC
        # @ATTRIBUTE f2 NUMERIC
        # @ATTRIBUTE class {1, 2}

        datautil.write_arff_header(feature_count=2, class_count=2, fout=m,
                comment='Comment', relation='wsd')

        expected_calls = [mock.call.write("% Comment\n"),
                mock.call.write("@RELATION wsd\n"),
                mock.call.write("@ATTRIBUTE f1 NUMERIC\n"),
                mock.call.write("@ATTRIBUTE f2 NUMERIC\n"),
                mock.call.write("@ATTRIBUTE class {1, 2}\n"),
                mock.call.write("\n"),
                mock.call.write("@DATA\n")]

        self.assertListEqual(m.mock_calls, expected_calls)


    def test_convert_index_line(self):
        m = mock_open()

        line = '41 42 2'

        datautil.convert_index_line(m, line)

        expected_output_calls = [mock.call.write('41, 42, 2'),
                mock.call.write('\n')]

        self.assertListEqual(m.mock_calls, expected_output_calls)


    def test_convert_index_file_to_arff(self):
        lines = """
        # Feature Count
        2
        # Class count
        2

        # Data
        1 2 1
        2 3 2
        """

        expected_output ="""% 
        @RELATION wsd
        @ATTRIBUTE f1 NUMERIC
        @ATTRIBUTE f2 NUMERIC
        @ATTRIBUTE class {1, 2}

        @DATA
        1, 2, 1
        2, 3, 2
        """




        fin = "/tmp/datautil.1.fin.txt"
        fout = "/tmp/datautil.1.fout.txt"

        with open(fin, "w") as f:
            f.write(lines)

        datautil.convert_index_file_to_arff(fin, fout)

        with open(fout) as f:
            expected_lines = expected_output.split("\n")

            for i, l in enumerate(f):
                self.assertEqual(l.strip(), expected_lines[i].strip())



# Shamelessly copied from Mock website:
# http://www.voidspace.org.uk/python/mock/examples.html#mocking-open
def mock_open(mock=None, data=None):
    file_spec = file
    if mock is None:
        mock = MagicMock(spec=file_spec)

    handle = MagicMock(spec=file_spec)
    handle.write.return_value = None
    if data is None:
        handle.__enter__.return_value = handle
    else:
        handle.__enter__.return_value = data
    mock.return_value = handle
    return mock


