# Compile
javac -cp .:lib/weka.jar Learn.java

# Train
java -cp .:lib/weka.jar Learn train /tmp/input.arff /tmp/classifier.serialized

# Test
java -cp .:lib/weka.jar Learn test /tmp/classifier.serialized /tmp/test.arff /tmp/output.txt
