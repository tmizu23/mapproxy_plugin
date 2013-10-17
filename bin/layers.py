import sys, yaml

str = open(sys.argv[1]).read()
yd = yaml.load(str)
print yd