
import weka.core.converters.ConverterUtils.DataSource;
import weka.classifiers.Classifier;
import weka.core.Instances;
import weka.core.Utils;

import weka.classifiers.trees.J48;

import java.io.PrintWriter;
import java.io.FileWriter;

class Util {
    public static Instances getData(String dataFile) throws Exception {
        /*
         * Reads from ARFF file.
         *
         * param
         * ----
         *  dataFile: Input file path.
         *
         * returns
         * ----
         *  Data instances.
         *
         */

        DataSource dSource = new DataSource(dataFile);
        Instances data = dSource.getDataSet();
        if (data.classIndex() == -1)
            data.setClassIndex(data.numAttributes() - 1);

        return data;
    }

    public static void formatOutputToKaggle(PrintWriter writer, int numberOfClass,
            int classifierOutput) {
        /**
         * Formats the classifier output to kaggle format.
         *
         * For k possible classes, there should be k + 1 lines where the first
         * line is always zero and predicted word-sense class is set to zero.
         *
         * params
         * ----
         *  writer: PrintWriter instance.
         *  numberOfClass: Total number of classes.
         *  classifierOutput: The nominal class predicted by the classifier.
         */
        for(int i = 0; i <= numberOfClass; i++) {
            if (i != classifierOutput)
                writer.println("0");
            else
                writer.println("1");
        }
    }
}

class Train {
    /*
     * Build classifier by training on instance data.
     */

    private Classifier classifier;
    private Instances trainInstances;

    public Train(String [] args) throws Exception {
        /* Constructs classifier by using options from the string array.
         *
         * param
         * ----
         *  args: Array of options. The following flags are in use:
         *      -S => File path to output serialized classifier.
         *      -F => Train arff file.
         *      -C => Classifier name and options. If no classifier is
         *          specified, J48() is used by default.
         */


        String trainFilePath = Utils.getOption('F', args);
        String outputPath = Utils.getOption('S', args);
        String classifierName = Utils.getOption('C', args);
        if (classifierName.length() == 0)
            new Train(trainFilePath, outputPath);
        else {
            Classifier classifier = Classifier.forName(classifierName,
                    args);

            new Train(trainFilePath, outputPath, classifier);
        }
    }

    public Train(String trainFilePath, String outputPath)
        throws Exception {
        /*
         * Performs the default tasks. It first created a classifier
         * to train on the dataset and then the classifier is serialized
         * to the given file.
         * param
         * ----
         *  trainFilePath: Training file location.
         *  outputPath: File path to which the classifier would be
         *      serialized.
         */

        this.setDataInstances(trainFilePath);
        this.buildClassifier();
        this.saveClassifier(outputPath);
    }

     public Train(String trainFilePath, String outputPath,
             Classifier classifier) throws Exception {
        /*
         * Performs the default tasks. It first created a classifier
         * to train on the dataset and then the classifier is serialized
         * to the given file.
         * param
         * ----
         *  trainFilePath: Training file location.
         *  outputPath: File path to which the classifier would be
         *      serialized.
         *  classifier: Classifier instance.
         */

        this.setDataInstances(trainFilePath);
        this.buildClassifier(classifier);
        this.saveClassifier(outputPath);
    }


    public void setDataInstances(String filename) throws Exception {
        this.trainInstances = Util.getData(filename);
    }

    public void buildClassifier(Classifier classifier)
        throws Exception {
        /*
         * Builds classifier.
         *
         * param
         * ----
         *  classifier: Classifier to be used for this class.
         */

        classifier.buildClassifier(this.trainInstances);
        this.classifier = classifier;
    }


    public void buildClassifier(Classifier classifier, 
            String options) throws Exception {
        /*
         * Builds classifier.
         *
         * param
         * ----
         *  classifier: Classifier to be used for this class.
         *  options: String options to be used.
         *
         */

        classifier.setOptions(weka.core.Utils.splitOptions(options));
        classifier.buildClassifier(this.trainInstances);
        this.classifier = classifier;
    }

    public void buildClassifier() throws Exception {

        /*
         * Default classifier with J48() tree.
         */
        Classifier classifier = new J48();
        String options = "-C 0.25 -M 2";

        this.buildClassifier(classifier, options);
    }

    public void saveClassifier(String outputPath) throws Exception {
        /*
         * Serialize classifier to a file.
         *
         * param
         * ----
         *  outputPath: The file path.
         */

        weka.core.SerializationHelper.write(outputPath, this.classifier);
    }

}

class Evaluate {

    /*
     * Evaluates the test instances.
     */

    private Classifier classifier;
    private Instances testInstances;

    public Evaluate(String args[]) throws Exception {
        /* Peforms evaluation by using options from the string array.
         *
         * param
         * ----
         *  args: Array of options. The following flags are in use:
         *      -S => Serialized classifier file.
         *      -F => Test arff file.
         *      -E => Output path to write evaluation result in kaggle
         *          format.
         */

        String serializedOutput = Utils.getOption('S', args);
        String testFilePath = Utils.getOption('F', args);
        String outputPath = Utils.getOption('E', args);

        new Evaluate(serializedOutput, testFilePath, outputPath);
    }

    public Evaluate(String serializedOutput, String testFilePath,
            String outputPath) throws Exception {
        /*
         * Performs default tasks. It deserializes the classifier
         * then write the evaluation data to the file.
         * param
         * ----
         *  serializedOutput: File path of the serialized output.
         *  testFilePath: Location of test data.
         *  outputPath: Output file location.
         */

        this.setSerializedClassifier(serializedOutput);
        this.setDataInstances(testFilePath);
        this.evaluateData(outputPath);
    }

    public void setSerializedClassifier(String serializedOutput)
        throws Exception {

        /*
         * Deserialized classifier. See the saveClassifier() method
         * in the Tran class.
         */
        Classifier cls = (Classifier) weka.core.SerializationHelper.read(
                serializedOutput);

        this.classifier = cls;
 
    }

    public void setDataInstances(String filename) throws Exception {
        this.testInstances = Util.getData(filename);
    }

    public void evaluateData(String outputPath) throws Exception {
        /*
         * Classify test instances and write each output in a single
         * line to the output file.
         *
         * param
         * ----
         *  outputPath: Path to the output file.
         */

        PrintWriter outputStream = null;

        try {
            outputStream = new PrintWriter(new FileWriter(outputPath));

            for (int i = 0; i < this.testInstances.numInstances(); i++) {
                double classLabel = this.classifier.classifyInstance(
                        this.testInstances.instance(i));

                Util.formatOutputToKaggle(outputStream,
                        this.testInstances.numClasses(), (int) classLabel);
            }

        } finally {
            if (outputStream != null) {
                outputStream.close();
            }
        }
    }
}

public class Learn {
    public static void main(String args[]) throws Exception {
        String helpString = "Usage: Learn -J [train|test] "
            + "-S serialized-file-location -F arff-file "
            + "[-E evaluation-output] [-C classifierName] "
            + "[classifier-options]\n";
        String job = Utils.getOption('J', args);

        if (job.length() == 0) {
            throw new Exception(helpString + "\n" +
                    "No Job description given.");
        } else if (job.equals("train"))
            new Train(args);
        else if (job.equals("test"))
            new Evaluate(args);
        else
            throw new Exception(helpString + "\n" +
                    "Unknown Job description given.");
    }
}


