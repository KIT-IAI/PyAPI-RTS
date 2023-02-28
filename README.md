# PyAPI-RTS

**A Python library to read and manipulate RSCAD draft files.**

See <a href="examples/simple_example/simple_example.ipynb">examples/simple_example/simple_example.ipynb</a> for a short preview of the API or take a look into our <a href="docs/pyapi_rts.pdf">documentation</a>.

## Installation

To install this project, perform the following steps:

1. Clone the project
2. `cd` into the cloned directory
3. `pip install poetry`
4. `poetry install`

## Generate classes from RSCAD components

Before the first use of the project, the classes for the components in the RSCAD master library need to be generated.

1. Copy the files from the `COMPONENTS` directory into `pyapi_rts/pyapi_rts/class_extractor/COMPONENTS`.

2. Run `poetry run python ./pyapi_rts/class_extractor/main.py`

Other options for the class generation:

- \-d: Set to delete the output folder before new classes are generated
- \-o: Set to include the OBSOLETE folder in the generation. Recommended if you use .dfx files converted from older versions
- \-p: Set path to COMPONENTS folder
- \-t: Set thread count used to parse the files. Default: 8 

! The progress bar is not accurate due to optimizations applied during generation.

## Run tests

`poetry run pytest`
