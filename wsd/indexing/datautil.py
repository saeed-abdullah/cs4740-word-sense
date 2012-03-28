
def get_data_line(filename, comment='#'):
    """
    Returns non-empty line which does not starts with comment character.

    params
    ----
    filename: Name of the file.
    comment: Comment character.

    returns
    ----
    A generator object that iterates over non-empty lines which are not
    comments.
    """
    with open(filename) as f:
        for l in f:
            line = l.strip()
            if len(line) > 0 and not line.startswith(comment):
                yield line



def write_arff_header(fout, feature_count, class_count, comment, relation):
    """Writes header information for ARFF format.

    There are two important assumptions about the dataset:
        * Feature count is fixed over the dataset --- no unknown values.
        * The class symbols are [1, class_count].

    params
    ----
    fout: The output file object.
    feature_count: Number of features per feature vector.
    class_count: Total number of class.
    comment: Comment to be written in the header.
    relation: Relation name.
    """

    comment_string = "% {0}\n"
    relation_string = "@RELATION {0}\n"

    feature_string = "@ATTRIBUTE f{0} NUMERIC\n"
    class_string = "@ATTRIBUTE class {{{0}}}\n"


    # Write the header string
    fout.write(comment_string.format(comment))
    fout.write(relation_string.format(relation))

    # Write the attribute strings
    for index in range(1, feature_count + 1):
        fout.write(feature_string.format(index))

    class_list = [str(x) for x in range(1, class_count + 1)]

    # Wtite class string
    fout.write(class_string.format(", ".join(class_list)))

    # Write Data section
    fout.write("\n")
    fout.write("@DATA\n")


def convert_index_line(fout, line):
    """Converts index data to feature vectors.

    Each feature in the index data is seperated by whitespaces and the
    last token denotes the class variable. As the word feature are
    already converted into numeric features, this function essentially
    changes comma as a delimiter instead of spaces.

    param
    ----
    fout: Output file objec.
    line: Index data, each feature is seperated by whitespaces and
        the class variable is the last token.
    for more details.
    """

    l = line.split()


    fout.write(", ".join(l))
    fout.write("\n")


def convert_index_file_to_arff(fin, fout, comment='', relation='wsd'):
    """Converts index data to ARFF format.

    param
    ----
    fin: Input file name.
    fout: Output filename.
    comment: Comment to be used in the header.
    relation: Relation name.
    """

    data_lines = get_data_line(fin)

    # The first line is the feature count
    feature_count = int(data_lines.next())

    # Second line is the class count
    class_count = int(data_lines.next())

    with open(fout, "w") as f:

        write_arff_header(fout=f, comment=comment, relation=relation,
            feature_count=feature_count, class_count=class_count)

        for line in data_lines:
            convert_index_line(f, line)


def generate_run_script(train_dir, test_dir, model_dir, evaluation_dir,
        script_filepath, java_command="java -cp .:weka.jar Learn",
        classifier_command=None):
    """Generates run script to train and test classifiers.

    This function writes a script file which contains two lines per arff test
    files to train a classifier over data in the train directory.

    So, given that there is a file named 'begin.v.arff' in the test directory,
    it will look for file with same name in the train directory to train
    a model given the classifier command. It will save the model in
    the model_dir and the output in kaggle format is saved to
    evaluation_dir.

    param
    ----
    train_dir: Directory containing training arff files.
    test_dir: Directory containing test arff files.
    model_dir: Directory to write serialized models.
    evaluation_dir: Directory to write evaluation output.
    script_filepath: File path of the script.
    java_command: The java command to run the classifier --- it should contain
        the lib locations and the class name.
    classifier_command: The classifier names and the options to pass to the
        java program.
    """

    train_string = "{0} -J train -F {1} -S {2} -C {3}"
    test_string = "{0} -J test -F {1} -S {2} -E {3}"

    import glob
    import os

    arff_file_wildcard = "*.arff"

    with open(script_filepath, "w") as f:
        # List all the arff files in the test directory.
        for test_file in glob.iglob(os.path.join(test_dir,
                arff_file_wildcard)):

            # Get the filename.
            arff_file_name = os.path.split(test_file)[1]

            train_file_path = os.path.join(train_dir, arff_file_name)
            model_file_path = os.path.join(model_dir, 
                    arff_file_name + ".model")
            evaluation_file_path = os.path.join(evaluation_dir,
                    arff_file_name + ".output")

            # Make sure that the train file for corresponding word
            # exists.
            if os.path.exists(train_file_path):
                train_command = train_string.format(java_command,
                        train_file_path, model_file_path,
                        classifier_command)

                test_command = test_string.format(java_command,
                        test_file, model_file_path, evaluation_file_path)

                # Write train command.
                f.write(train_command)
                f.write("\n")

                # Write test command.
                f.write(test_command)
                f.write("\n")

            else:
                print "No training file: " + train_file_path


if __name__ == "__main__":
    train_dir = "train_arffs/"
    test_dir = "test_arffs/"
    model_dir = "model/"
    evaluation_dir = "evaluate/"
    run_script = "run_script.sh"

    java_command = "java -cp .:lib/weka.jar Learn"
    classifier_command = "weka.classifiers.functions.SMO " +\
        "-C 2.0 -L 0.0010 -P 1.0E-12 -N 0 -V -1 -W 1 -K " +\
        '"weka.classifiers.functions.supportVector.RBFKernel -C ' +\
        '250007 -G 0.0"'

    generate_run_script(train_dir, test_dir, model_dir,
            evaluation_dir, run_script, java_command, classifier_command)

