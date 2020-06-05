from generator import Configs, Generator, GeneratorError

from datetime import timedelta
import argparse
import logging
import pytest
import time


@pytest.fixture
def generator():
    configs = Configs(4, 2, 4)
    return Generator(configs)


@pytest.fixture
def partitions(generator):
    return generator.make_partitions()


@pytest.fixture
def partitions_with_leaders(generator, partitions):
    return [x for x in generator.combine_partitions_with_leaders(partitions)]


@pytest.fixture
def testcases(generator, partitions_with_leaders):
    testcases = generator.combine_scenarios_with_rounds(
        partitions_with_leaders
    )
    return [x for x in testcases]


def test_make_config_bad_inputs():
    with pytest.raises(GeneratorError):
        _ = Configs(2, -2, 8)


def test_make_generator_bad_inputs():
    configs = Configs(4, 2, 8)
    with pytest.raises(GeneratorError):
        _ = Generator(configs, -3, '')


def test_make_partitions():
    generator = Generator(Configs(4, 2, 8))
    partitions = generator.make_partitions()
    assert partitions == [
        [[0, 1, 2, 3], [4]],
        [[0, 1, 2, 4], [3]],
        [[0, 1, 3, 4], [2]],
        [[0, 2, 3, 4], [1]],
        [[0, 3, 4], [1, 2]],
        [[0, 1, 4], [2, 3]],
        [[0, 2, 4], [1, 3]],
        [[0, 4], [1, 2, 3]],
        [[0, 1, 2], [3, 4]],
        [[0, 1, 3], [2, 4]],
        [[0, 2, 3], [1, 4]],
        [[0, 3], [1, 2, 4]],
        [[0, 1], [2, 3, 4]],
        [[0, 2], [1, 3, 4]],
        [[0], [1, 2, 3, 4]],
    ]


def test_combine_partitions_with_leaders(generator, partitions):
    scenarios = generator.combine_partitions_with_leaders(partitions)
    length = len(partitions) * len(generator.target_nodes)
    assert len([s for s in scenarios]) == length


def test_combine_scenarios_with_rounds(generator, partitions_with_leaders):
    testcases = generator.combine_scenarios_with_rounds(
        partitions_with_leaders
    )
    length = len(partitions_with_leaders) ** generator.configs.number_of_rounds
    assert len([x for x in testcases]) == length


def test_forecast_number_of_testcases(generator, testcases):
    assert len(testcases) == generator.forecast_number_of_testcases()


def test_print():
    # TODO
    assert True


#@pytest.mark.skip(reason='Performance benchmark.')
def test_performance():
    generator = Generator(Configs(4, 2, 8))
    print(f'Generating {generator.forecast_number_of_testcases()} testcases..')
    start_time = time.time()
    generator.run(dryrun=True)
    elapsed_time = time.time() - start_time
    print(f'Elapsed time: {str(timedelta(seconds=elapsed_time))}')


if __name__ == '__main__':
    """ Simple cli interface. """
    parser = argparse.ArgumentParser(description='Twins Generator.')
    parser.add_argument(
        '--nodes', help='the number of nodes', type=int
    )
    parser.add_argument(
        '--partitions', help='the number of partitions', type=int
    )
    parser.add_argument(
        '--rounds', help='the number of rounds', type=int
    )
    parser.add_argument(
        '--testcases_per_file',
        help='number of testcases to print per file (default 100)',
        type=int,
        default=100
    )
    parser.add_argument(
        '--path',
        help='directory path where to print the testcases (default "./")',
        default='./'
    )
    parser.add_argument(
        '-v', dest='verb', action='store_true', help='activate verbose logging'
    )
    args = parser.parse_args()

    if args.nodes is None or args.partitions is None or args.rounds is None:
        parser.error(
            'arguments "nodes", "rounds", and "partitions" must be supplied'
        )
    if args.nodes <= 0 or args.partitions <= 0 or args.rounds <= 0:
        parser.error(
            'arguments "nodes", "rounds", and "partitions" must be positif'
        )
    if args.testcases_per_file <= 0:
        parser.error(
            'argument "testcases_per_file" must be positif'
        )

    logging.basicConfig(
        level=logging.DEBUG if args.verb else logging.INFO,
        format="[%(levelname)s] %(asctime)s: %(message)s"
    )

    configs = Configs(args.nodes, args.partitions, args.rounds)
    generator = Generator(configs, args.testcases_per_file, args.path)
    generator.run()
