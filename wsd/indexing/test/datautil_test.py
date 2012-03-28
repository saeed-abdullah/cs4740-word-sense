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


    def test_generate_run_script(self):

        import tempfile
        import os

        # Create a temporary directory with test and train files.
        tmp_dir = tempfile.mkdtemp()
        temp_test_dir = os.path.join(tmp_dir, "test/")
        temp_train_dir = os.path.join(tmp_dir, "train/")
        model_dir = os.path.join(tmp_dir, "model/")
        evaluation_dir = os.path.join(tmp_dir, "evaluation/")
        java_command = "java -cp .:weka.jar Learn"
        classifier_command = "weka.classifiers.functions.SMO " +\
            "-C 2.0 -L 0.0010 -P 1.0E-12 -N 0 -V -1 -W 1 -K " +\
            '"weka.classifiers.functions.supportVector.RBFKernel -C ' +\
            '250007 -G 0.0"'

        # Create directory
        os.mkdir(temp_test_dir)
        os.mkdir(temp_train_dir)

        expected_train_line = "{0} -J train -F {{0}} -S {{1}} -C {1}".format(
            java_command, classifier_command)
        expected_test_line = "{0} -J test -F {{0}} -S {{1}} -E {{2}}".format(
            java_command)

        expected_calls = []


        # Create fake arff files.
        arff_files = ["bank.n.arff", "begin.v.arff"]
        for arff_file in arff_files:
            train_file_name = os.path.join(temp_train_dir, arff_file)
            test_file_name = os.path.join(temp_test_dir, arff_file)
            model_file_name = os.path.join(model_dir, arff_file + ".model")
            evaluation_file_name = os.path.join(evaluation_dir,
                arff_file + ".output")

            open(train_file_name, "w")
            open(test_file_name, "w")

            expected_calls.append(mock.call().write(
                expected_train_line.format(train_file_name, model_file_name)))
            expected_calls.append(mock.call().write("\n"))
            expected_calls.append(mock.call().write(
                expected_test_line.format(test_file_name, model_file_name,
                    evaluation_file_name)))
            expected_calls.append(mock.call().write("\n"))

        m = mock_open()
        open_name = "{0}.open".format(datautil.__name__)
        with patch(open_name, m, create=True):
            datautil.generate_run_script(temp_train_dir, temp_test_dir,
                    model_dir, evaluation_dir, "", java_command,
                    classifier_command)

        # First mock call open and second call is for block entry
        # while the last call is for block exit. So, these three
        # calls are overlooked.
        self.assertListEqual(m.mock_calls[2:-1], expected_calls)

        import shutil
        shutil.rmtree(tmp_dir)


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


