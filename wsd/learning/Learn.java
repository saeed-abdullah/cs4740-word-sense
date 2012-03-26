
import weka.core.converters.ConverterUtils.DataSource;
import weka.classifiers.Classifier;
import weka.core.Instances;

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



    public void setDataInstances(String filename) throws Exception {
        this.trainInstances = Util.getData(filename);
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
         * Needs to re-implement this so that instead of supplying 
         * actual instance of classifier, a string name would suffice.
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
        String train = "train";
        String test = "test";
        if (args[0].equals(train)) {
            /* Performs training.
             * First param is the input source and the second param
             * is the serialization output path.
             */
            new Train(args[1], args[2]);
        } else if (args[0].equals(test)) {
            /* Evaluates the test data.
             * First param is the serialized classifier, second param
             * denotes data location and the third param is the output
             * path.
             */
            new Evaluate(args[1], args[2], args[3]);
        }
    }
}


