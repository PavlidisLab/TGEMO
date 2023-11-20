ROBOT := java -jar robot.jar

TGEMO.OBO: TGEMO.OWL
	$(ROBOT) convert --format obo --input $^ --output $@
