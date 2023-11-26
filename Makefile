ROBOT := java -jar robot.jar

all: TGEMO.OBO

TGEMO.OBO: TGEMO.OWL
	$(ROBOT) convert --format obo --input $^ --output $@

check: TGEMO.OWL
	$(ROBOT) validate-profile --profile Full --input $^

.PHONY: all check
