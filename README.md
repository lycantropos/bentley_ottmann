bentley_ottmann
===============

[![](https://github.com/lycantropos/bentley_ottmann/workflows/CI/badge.svg?branch=master)](https://github.com/lycantropos/bentley_ottmann/actions/workflows/ci.yml "Github Actions")
[![](https://readthedocs.org/projects/bentley_ottmann/badge/?version=latest)](https://bentley-ottmann.readthedocs.io/en/latest "Documentation")
[![](https://codecov.io/gh/lycantropos/bentley_ottmann/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/bentley_ottmann "Codecov")
[![](https://img.shields.io/github/license/lycantropos/bentley_ottmann.svg)](https://github.com/lycantropos/bentley_ottmann/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/bentley-ottmann.svg)](https://badge.fury.io/py/bentley-ottmann "PyPI")

In what follows `python` is an alias for `python3.7` or `pypy3.7`
or any later version (`python3.8`, `pypy3.8` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions
```bash
python -m pip install --upgrade pip setuptools
```

### User

Download and install the latest stable version from `PyPI` repository
```bash
python -m pip install --upgrade bentley_ottmann
```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/bentley_ottmann.git
cd bentley_ottmann
```

Install dependencies
```bash
python -m pip install -r requirements.txt
```

Install
```bash
python setup.py install
```

Absolutely, here's a comprehensive `Usage` section for the README documentation of your Bentley-Ottmann algorithm repository:

---

## Usage

The Bentley-Ottmann algorithm implemented in this repository is a robust method for detecting intersections in a set of line segments. It's particularly efficient for large sets of segments, offering a sweep line based approach for intersection detection. This section guides you through the basic usage of the different components of this algorithm.

### Setting Up the Environment

To use the Bentley-Ottmann implementation, first import the necessary modules from the `bentley_ottmann.core` package:

```python
from bentley_ottmann.core import sweep, LeftEvent, Segment, Point
```

### Preparing the Data

Prepare your line segments by creating instances of `Segment`. Each `Segment` consists of two `Point` objects representing its start and end:

```python
# Example segments
segments = [
    Segment(Point(0, 0), Point(1, 1)),
    Segment(Point(1, 0), Point(0, 1)),
    # Add more segments as needed
]
```

### Running the Algorithm

Invoke the `sweep` function from the `base` module with your segments. The function yields `LeftEvent` objects, representing events on the left endpoints of the segments:

```python
# Processing the segments
for event in sweep(segments, context=YourContextImplementation):
    # Handle or inspect the event
    print(f"Processed event at: {event.start}")
```

### Advanced Usage

For more advanced usage, you can directly interact with other components of the algorithm:

- **EventsQueue**: Manages the priority queue of events during the sweep-line process.
- **SweepLine**: Maintains the state of the sweep line, tracking segments currently intersecting with the sweep line.
- **Utilities**: Offers helper functions like `all_unique`, `classify_overlap`, and `to_sorted_pair` for geometric computations.

Example of interacting with the SweepLine:

```python
from bentley_ottmann.core import SweepLine

sweep_line = SweepLine(your_context)
for segment in segments:
    sweep_line.add(segment)
    # Additional processing and updates to the sweep line
    sweep_line.remove(segment)
```

### Context Implementation

The algorithm requires a `Context` that can be found in `ground.base` which is supplied in [this repository](https://github.com/lycatropos/ground)

### Examples

For a more hands-on approach, refer to the example usage in the docstrings of each module, demonstrating specific functionalities and their applications in the context of the Bentley-Ottmann algorithm.

---

This section aims to provide users with clear and concise instructions on how to utilize the various components of your Bentley-Ottmann algorithm implementation, ensuring a smooth integration into their projects or studies involving computational geometry.

Development
-----------

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose release
```

Bump version
```bash
bump2version --verbose release
```

This will set version to `major.minor.patch`.

### Running tests

Install dependencies
```bash
python -m pip install -r requirements-tests.txt
```

Plain
```bash
pytest
```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script:
- with `CPython`
  ```bash
  ./run-tests.sh
  ```
  or
  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`
  ```bash
  ./run-tests.sh pypy
  ```

`PowerShell` script:
- with `CPython`
  ```powershell
  .\run-tests.ps1
  ```
  or
  ```powershell
  .\run-tests.ps1 cpython
  ```
- with `PyPy`
  ```powershell
  .\run-tests.ps1 pypy
  ```
