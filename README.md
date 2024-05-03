# imgparallel

A toolbox for pre-processing and formatting image datasets.

`imgparallel` is a command line interface and python library for processing image datasets stored as individual files. Currently the tool exists as an MVP, supporting very minimal transforms and limited flexibility.

## Installation

### From PyPI

```
pip install imgparallel
```

### From Source

```
git clone https://github.com/jackson-waschura/imgparallel.git
cd imgparallel/
pip install -e .
```

## Examples

Here is an example usage which resizes all images from `test_data/input_images` to `512x512` then saves them to `test_data/output_images` as jpegs.

```
imgparallel --src test_data/input_images --dst test_data/output_images --resize 512x512 --format jpg --proc_per_stage 1
```

The CLI can also be invoked like this:

```
python3 imgparallel/cli.py --src test_data/input_images --dst test_data/output_images --resize 512x512 --format jpg --proc_per_stage 1
```

## To Do

 - [X] Implement a simple MVP CLI tool for reformatting an image dataset (image format, resize)
 - [X] Evaluate the output of running the tool
 - [X] Implement sanity checks / tests for permissions before running the pipeline.
 - [X] Add an alias / script into the package so it can be run by name from anywhere
 - [X] Implement tests to evaluate correctness of the tool
 - [ ] Use wheel and twine to publish the MVP tool
 - [ ] Draft a design for more complex transforms (multiple resolution outputs, cropping, etc)
