

## Generating visualizations

## Running tests

### Unit tests
The gradle project has a few unit tests that test the correctness of the different functions. To run them, execute these terminal commands:
```zsh
cd hyperloglog
./gradlew test
```

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

