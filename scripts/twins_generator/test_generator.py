from generator import Configs, Generator

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
    with pytest.raises(TypeError):
        _ = Configs(2, 'a', 8)

    with pytest.raises(ValueError):
        _ = Configs(2, -2, 8)


def test_make_generator_bad_inputs():
    configs = Configs(4, 2, 8)
    with pytest.raises(TypeError):
        _ = Generator(configs, testcases_per_file='a')

    with pytest.raises(ValueError):
        _ = Generator(configs, machine_index=-1)


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


def test_testcases_length(generator, testcases):
    assert len(testcases) == generator.testcases_length


def test_print():
    # TODO
    assert True


@pytest.mark.skip(reason='Performance benchmark.')
def test_performance():
    generator = Generator(Configs(4, 2, 5), testcases_per_file=100)
    print(f'Generating {generator.testcases_length} testcases..')
    start_time = time.perf_counter()
    generator.run(dryrun=True, workers=8)
    elapsed_time = time.perf_counter() - start_time
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
        '--index',
        help='the index of the machine (default "1")',
        type=int,
        default=1
    )
    parser.add_argument(
        '--machines',
        help='the total number of machines (default "1")',
        type=int,
        default=1
    )
    parser.add_argument(
        '--workers',
        help='the number of processes (default "1")',
        type=int,
        default=1
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
            'argument "testcases_per_file" must be strictly positif'
        )
    if args.index <= 0 or args.index > args.machines:
        parser.error(
            'invalid machine index or number of machines'
        )
    if args.workers <= 0:
        parser.error(
            'argument "workers" must be strictly positif'
        )

    logging.basicConfig(
        level=logging.DEBUG if args.verb else logging.INFO,
        format="[%(levelname)s] %(asctime)s: %(message)s"
    )

    configs = Configs(args.nodes, args.partitions, args.rounds)
    generator = Generator(
        configs,
        filter=None,
        testcases_per_file=args.testcases_per_file,
        folder_path=args.path,
        machine_index=args.index,
        number_of_machines=args.machines
    )
    generator.run(workers=args.workers, dryrun=True)
