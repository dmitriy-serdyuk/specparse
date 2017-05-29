from configurator import ConfigurationParser


def test_no_modes():
    parser = ConfigurationParser()

    args = parser.parse_args(['conf.yaml'])
    #TODO: check args


def test_modes():
    parser = ConfigurationParser()
    train_parser = parser.add_mode('train', train)
    train_parser.add_argument('--hello', type=int, required=True)

    args = parser.parse_args(['train', '--hello', '89', 'conf.yaml'])
    #TODO: check args


def test_changes():
    pass


def test_inheritance():
    pass
