from numpy.testing import assert_almost_equal

from specparse import SpecificationParser


def test_no_modes():
    parser = SpecificationParser()

    args = parser.parse_args(['examples/experiment1.yaml'])
    assert_almost_equal(1.e-4, args['learning_rate'])
    assert args['network']['type'] == "LSTM"
    assert 'cmd_args' in args

    parser = SpecificationParser()
    parser.add_argument('--restart-from')

    exp_dir = 'exp/exp01'
    args = parser.parse_args(
        ['examples/experiment1.yaml', '--restart-from', exp_dir])
    assert_almost_equal(1.e-4, args['learning_rate'])
    assert args['network']['type'] == "LSTM"
    assert args['cmd_args']['restart_from'] == exp_dir


def test_modes():
    def train(learning_rate, network, cmd_args):
        return learning_rate, network, cmd_args
    parser = SpecificationParser()
    train_parser = parser.add_mode('train', train)
    train_parser.add_argument('--hello', type=int, required=True)

    arg_list = ['examples/experiment1.yaml', 'train', '--hello', '89']
    args = parser.parse_args(arg_list)
    assert args['cmd_args']['hello'] == 89
    lr, net, _ = parser.parse_and_run(arg_list)
    assert_almost_equal(1.e-4, lr)
    assert net['type'] == "LSTM"


def test_changes():
    parser = SpecificationParser()

    args = parser.parse_args(
        ['examples/experiment1.yaml', 'learning_rate=1.e-6',
         'network.type=GRU'])
    assert_almost_equal(1.e-6, args['learning_rate'])
    assert args['network']['type'] == "GRU"
    assert 'cmd_args' in args


def test_inheritance():
    parser = SpecificationParser()

    args = parser.parse_args(['examples/experiment2.yaml'])
    assert_almost_equal(1.e-5, args['learning_rate'])
    assert args['network']['type'] == "LSTM"
    assert 'cmd_args' in args

