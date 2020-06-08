# Twins Generator
The Twin generator has been carefullly design to not have any external dependency, so it should work out of the box:
```
generator = Generator(4, 2, 8) # Create a generator instance with 4 nodes, 2 partitions and 8 rounds.
generator.run() # Run the generator to print testcases to files.
```
The generator can take many other optional arguments such as the maximum number of testcases to print per file or the number of processes. It also provide facilities to shard generation accross multiple (independent) machines. Detailed documentation can be found in the source file `generator.py`.

## Cli
The file `cli.py` provides a simple command line interface to run the generator, and takes `argparse` as dependency:
```
$ pip install argparse
$ python -O cli.py --nodes 4 --partitions 2 --rounds 4 --workers 16 -dryrun
```

## Test
If you have `pip` installed, you can install `pytest` with the following command:
```
$ pip install pytest
```
Then simply run:
```
$ pytest
```

## Benchmark
First install `matplotlib`:
```
$ pip install matplotlib
```
Then run one of the following commands:
```
$ python -O benchmark.py # Run a fast benchmark (should take a few seconds)
$ python -O benchmark.py plot # Run a full benchmark and plot results
```
