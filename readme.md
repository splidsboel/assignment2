# Instructions

Our implementation of hyperloglog is a gradle project with java code packaged into a .jar file. To package the .jar, run this command in the hyperloglog directory:
```zsh
./gradlew jar
```

We provide a few unit tests for testing correctness of the program. To run the unit tests, execute this command in the hyperloglog directory:
```zsh
./gradlew test
```


## Generating visualizations

For the report, we provide visualizations of the different experiments, we have run. This is a list of instructions to reproduce these visualizations

### rho-function
```zsh
# generate data
python experiments.py
# generate plot
python postprocess.py
```
The plot can be found [here](hyperloglog/rho_distribution.png)

### HyperLogLog error estimation
#### Histogram
```zsh
# run experiments and generate histogram
# --trials adjusts the amount of trials run during the experiment - default is 8 (for faster execution), table in report uses trias = 100.
python3 hll_experiment.py -n 100000 --seed 1 --trials 100
```
The histogram can be found [here](hyperloglog/hll_error_histogram.png)

#### Table
Generates a [.tex file](hyperloglog/estimation_error_table.tex)
```zsh
## commands --runs and --n-values are available for shorter smoke-test runs
python estimation_error_table.py
```


## Running tests

In addition to the unit tests in the gradle project, we also tested our implementation of hyperloglog against the data provided in the assignment description. Below are instructions to run the python scripts which test our implementation


### Python sample data scripts

We provide a few different python scripts to test our implementations against the provided sample data. Results will be printed to the terminal. 
All python scripts can be ran at once by running `make sample-tests`in the `hyperloglog`directory


#### Threshold:
```zsh
# run all tests
python test_threshold_sample_data.py

# run a specific test
python test_threshold_sample_data.py 02-BigTests
```

#### Rho:
```zsh
python test_hash_sample_data.py
```

#### Hash:
```zsh
python test_rho_sample_data.py 
```

#### Registers:
```zsh
python test_register_sample_data.py
```

