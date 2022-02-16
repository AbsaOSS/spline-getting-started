default: clean build
clean:
	find . -type d -name "target" | xargs rm -fr
build:
	sbt clean +assembly
