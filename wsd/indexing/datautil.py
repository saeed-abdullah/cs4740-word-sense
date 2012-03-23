
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


