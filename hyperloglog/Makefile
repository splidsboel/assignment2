SHELL := /bin/bash

JAVA_SOURCES := $(shell find app/src/main/java -name '*.java')
CLASSES_DIR := app/build/classes/java/main
JAR := app/build/libs/app.jar

.PHONY: sample-tests threshold-samples hash-samples rho-samples register-samples
.PHONY: build-jar clean

$(JAR): $(JAVA_SOURCES)
	@mkdir -p $(CLASSES_DIR)
	@mkdir -p $(dir $(JAR))
	javac -d $(CLASSES_DIR) $(JAVA_SOURCES)
	jar cfe $(JAR) hyperloglog.HyperLogLog -C $(CLASSES_DIR) .

build-jar: $(JAR)

threshold-samples: $(JAR)
	python3 test_threshold_sample_data.py

hash-samples: $(JAR)
	python3 test_hash_sample_data.py

rho-samples: $(JAR)
	python3 test_rho_sample_data.py

register-samples: $(JAR)
	python3 test_register_sample_data.py

sample-tests: threshold-samples hash-samples rho-samples register-samples

clean:
	rm -rf app/build
