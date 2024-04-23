# imgparallel

A toolbox for pre-processing and formatting image datasets.

TODO: longer description here

## Installation

TODO: Add installation instructions

## Examples

```
python3 imgparallel/cli.py --src test_data/input_images --dst test_data/output_images --resize 512x512 --format jpg --proc 1
```

## To Do

 - [X] Implement a simple MVP CLI tool for reformatting an image dataset (image format, resize)
 - [X] Evaluate the output of running the tool
 - [X] Implement sanity checks / tests for permissions before running the pipeline.
 - [X] Add an alias / script into the package so it can be run by name from anywhere
 - [X] Implement tests to evaluate correctness of the tool
 - [ ] Draft a design for better two-way communication with workers using per-worker pipes/queues
 - [ ] Draft a design for more complex transforms (multiple resolution outputs, cropping, etc)
 - [ ] Use wheel and twine to publish the MVP tool
 - [ ] Implement a GUI for evaluating conversions & transforms before running
