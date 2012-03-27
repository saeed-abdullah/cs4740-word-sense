# Compile
javac -cp .:lib/weka.jar Learn.java

# Train
java -cp .:lib/weka.jar Learn -J train -F /tmp/input.arff -S /tmp/classifier.serialized

# Test
java -cp .:lib/weka.jar Learn -J test -S /tmp/classifier.serialized -F /tmp/test.arff -E /tmp/output.txt

# Zero-R Train
java -cp .:lib/weka.jar Learn -J train -F /tmp/input.arff -S /tmp/zeror.serialized -C weka.classifiers.rules.ZeroR

# Test
java -cp .:lib/weka.jar Learn -J test -S /tmp/zeror.serialized -F /tmp/test.arff -E /tmp/zeror.output.txt
