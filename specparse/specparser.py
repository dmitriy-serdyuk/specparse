from __future__ import print_function
import argparse
import yaml
import os
import importlib
from collections import OrderedDict


class ParseChanges(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        setattr(args, self.dest, values)


class SpecificationParser(object):
    r"""Configuration parser.

    A smart extension over the argument parser which can read and modify
    yaml configs.

    Parameters
    ----------
    schema_path : str
        Path for a schema file. Defaults to `None`, the schema is not
        validated in this case. Requires `pykwalify` package.
    \*\*kwargs : dict
        Arguments to be passed to the `ArgumentParser`.

    Attributes
    ----------
    parser : :class:`ArgumentParser`
        The argument parser.

    modes : dict
        Named subparsers for different modes.

    """
    def __init__(self, schema_path=None, **kwargs):
        self.parser = argparse.ArgumentParser(**kwargs)
        self.schema_path = schema_path
        self.modes = OrderedDict()
        self._subparsers = None
        self.parser.add_argument('config_path', help='Configuration file path')

    def add_argument(self, *args, **kwargs):
        return self.parser.add_argument(*args, **kwargs)

    def _read_config(self, file_):
        """Reads a configuration from YAML file.

        Resolves parent links in the configuration.

        """
        config = yaml.load(file_)
        if 'parent' in config:
            with open(os.path.expandvars(config['parent'])) as src:
                changes = dict(config)
                config = self._read_config(src)
                self._merge_recursively(config, changes)
        return config

    def _merge_recursively(self, config, changes):
        """Merge hierarchy of changes into a configuration."""
        for key, value in changes.items():
            if isinstance(value, dict) and isinstance(config.get(key), dict):
                self._merge_recursively(config[key], value)
            else:
                config[key] = value

    def _prepare_config(self, cmd_args):
        # Experiment configuration
        original_cmd_args = dict(cmd_args)
        config_path = cmd_args.pop('config_path')
        config_changes = cmd_args.pop('config_changes')

        with open(config_path, 'rt') as src:
            config = self._read_config(src)
        self._make_config_changes(config, config_changes)

        # Validate the configuration and the training stages
        if self.schema_path:
            from pykwalify.core import Core
            with open(os.path.expandvars(self.schema_path)) as schema_file:
                schema = yaml.safe_load(schema_file)
                core = Core(source_data=config, schema_data=schema)
                core.validate(raise_exception=True)
        config = dict(config)

        config['cmd_args'] = original_cmd_args
        return config

    def _make_config_changes(self, config, changes):
        """Apply changes to a configuration.

        Parameters
        ----------
        config : dict
            The configuration.
        changes : dict
            A dict of (hierarchical path as string, new value) pairs.

        """
        for path_value in changes:
            path, value = path_value.split('=')
            parts = path.split('.')
            assign_to = config
            for part in parts[:-1]:
                assign_to = assign_to[part]
            assign_to[parts[-1]] = yaml.load(value)

    def add_mode(self, name, func=None, **kwargs):
        r"""Adds an experiment mode.

        Parameters
        ----------
        name : str
            Mode name. The subparser will have this name.
        func : callable
            A callback function for the mode. Defaults to `None`, in this
            case no callback is provided.
        \*\*kwargs : dict
            Keyword arguments to be passed to the subparser.

        Returns
        -------
        A subparser corresponding to the mode.

        """
        if self._subparsers is None:
            self._subparsers = self.parser.add_subparsers(
                help='Choices for modes')
        parser = self._subparsers.add_parser(name, **kwargs)
        if func is not None:
            parser.set_defaults(func=func)
        self.modes[name] = parser
        return parser

    def parse_args(self, args=None, namespace=None, log_spec=False):
        """Parse arguments and specification.

        Parameters
        ----------
        args : list
            Arguments for the argument parser.
        namespace : list
            Namespace for the argument parser.
        log_spec : bool
            Log the specification after parsing.

        """
        for parser in self.modes.values():
            parser.add_argument(
                "config_changes", default=[], action=ParseChanges, nargs='*',
                help="Changes to configuration. [<path>=<value>]")
        if not self.modes:
            self.parser.add_argument(
                "config_changes", default=[], action=ParseChanges, nargs='*',
                help="Changes to configuration. [<path>=<value>]")
        args = self.parser.parse_args(args, namespace)
        config = self._prepare_config(args.__dict__)
        if log_spec:
            print(yaml.dump(config))
        return config

    def parse_and_run(self, args=None, namespace=None, log_spec=False):
        """Parse arguments and specification, run the callback.

        Parameters
        ----------
        args : list
            Arguments for the argument parser.
        namespace : list
            Namespace for the argument parser.
        log_spec : bool
            Log the specification after parsing.

        """
        config = self.parse_args(args, namespace, log_spec)
        func = config['cmd_args']['func']
        if callable(func):
            return func(**config)
        elif isinstance(func, str):
            module = importlib.import_module('.'.join(func.split('.')[:-1]))
            return getattr(module, func.split('.')[-1])(**config)
        else:
            raise ValueError
