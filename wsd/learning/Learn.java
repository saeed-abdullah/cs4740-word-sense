i
import weka.core.converters.ConverterUtils.DataSource;
import weka.classifiers.Classifier;
import weka.core.Instances;

import weka.classifiers.trees.J48;

import java.io.PrintWriter;
import java.io.FileWriter;

class Util {
    public static Instances getData(string dataFile) throws Exception {
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
}

class Train {
    /*
     * Build classifier by training on instance data.
     */

    private Classifier classifier;
    private Instances trainInstances;


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

    public void buildClassifier() {

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

    public void setSerializedClassifier(String serializedOutput)
        throws Exception {

        /*
         * Deserialized classifier. See the saveClassifier() method
         * in the Tran class.
         */
        Classifier cls = (Classifier) weka.core.SerializationHelper.read(
                serialized);

        this.classifier = cls;
 
    }

    public void setDataInstances(String filename) throws Exception {
        this.trainInstances = Util.getData(filename);
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

            for (int i = 0; i < testInstances.numInstances; i++) {
                double classLabel = this.classifier.classifyInstance(
                        this.testInstances.instance(i))

                outputStream.println(classLabel);
            }

        } finally {
            if (outputStream != null) {
                outputStream.close();
            }
        }
    }
}


