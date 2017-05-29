Hierarchical YAML Configuration Parser
======================================

The aim of this project is to provide simple configurations. Mostly, it
is targeted for machine learning application where every experiment has 
following features
- has a number of hyper-parameters;
- can be run in different modes, for example, "train" and "test".

Additionally, researches frequently want to
- easily run new versions of old experiments;
- alter configurations from the command line to poke around.

Given this desiderata, this project provides a wrapper around the 
`ArgumentParser` from `argparse` package which can read YAML configurations.

The proposed experiment structure is following:
- the hyper-parameters are stored in YAML format.

  For example, we can to describe a two layer LSTM model as
  ```yaml
  # experiment1.yaml:
  learning_rate: 1e-4  # the learning rate for training
  network:
    type: LSTM  # network type
    layers: 2  # number of layers
  ```
- a YAML file can be inherited from another one.

  For example, we found that the above experiment diverges, the learning
  rate should be decreased
  ```yaml
  # experiment2.yaml:
  parent: experiment1.yaml
  learning_rate: 1e-5
  ```
- the configuration is parsed and provided to the script as a dictionary,
  similarly to `argparse`;
- the configuration can be altered from the command line

  The same configuration
  as in `experiment2.yaml` can be obtained when the main script is run as
  ```bash
  train.py experiment1.yaml learning_rate=1e-5
  ```
- the script may have several "modes" of running

  This is similar to `subparsers` from `argparse`. 
  
  

Usage
-----

First, we create the a simple yaml configuration:

```python
>>> with open('conf.yaml', 'wb') as f:
...     _ = f.write(b"parameter_a: 42")
```

Then, we create a parser and feed it the config file name:

```python
>>> parser = ConfigurationParser()
>>> args = parser.parse_args(['conf.yaml'])
>>> print(args['parameter_a'])
42
>>> print(args['cmd_args']['config_path'])
conf.yaml
```

Defaults from the config can be changed from the command line,
this corresponds to a call like
```bash
your_script.py conf.yaml parameter_a=43
```

```python
>>> parser = ConfigurationParser()
>>> args = parser.parse_args(['conf.yaml', 'parameter_a=43'])
>>> print(args['parameter_a'])
43
```

Elements in the dictionary are accessed with the dot notation as
`dictionary.element=new_value`.

### Inheritance

Frequently a configuration for a given experiment is just a slight
modification of a previous one. To avoid code duplication this package
provides means to alter the configuration.

A yaml configuration file can be inherited from another file. The `parent`
field instructs the parser to read the parent configuration file first,
then update the child. For example, given two files
```yaml
# conf_base.yaml:
encoder_parameters:
    shape: 40
    type: raw_features
# conf_child.yaml:
parent: conf_base.yaml
encoder_parameters:
    shape: 50
```
The resulting configuration is equivalent to
```yaml
encoder_parameters:
    shape: 50
    type: raw_features
```

Note that the dictionary is updated, not rewritten, therefore the `type`
field stays untouched.

### Modes

This feature helps to maintain several modes for the experiment, such
as `create_data`, `train`, `test`, `generate`, and so on.

```python
>>> parser = ConfigurationParser()
>>> train_parser = parser.add_mode('train')
>>> _ = train_parser.add_argument('--checkpoint-dir')
>>> args = parser.parse_args(
...     ['conf.yaml', 'train', '--checkpoint-dir', './models/'])
>>> print(args['checkpoint_dir'])
./models/
```

### Callback Functions
