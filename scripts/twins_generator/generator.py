import logging
from itertools import product, zip_longest
from more_itertools import ichunked
from os.path import join
from copy import deepcopy
from math import ceil, factorial as f
from threading import Thread


class GeneratorError(Exception):
    pass


class Configs:
    def __init__(self, number_of_nodes, number_of_partitions, number_of_rounds):
        ok = isinstance(number_of_nodes, int)
        ok &= number_of_nodes > 0
        ok &= isinstance(number_of_partitions, int)
        ok &= number_of_partitions > 0
        ok &= isinstance(number_of_rounds, int)
        ok &= number_of_rounds > 0
        if not ok:
            raise GeneratorError('Bad input arguments.')

        self.number_of_nodes = number_of_nodes
        self.number_of_partitions = number_of_partitions
        self.number_of_rounds = number_of_rounds

    def __str__(self):
        return (
            f'(number of nodes: {self.number_of_nodes}, '
            f'number of partitions: {self.number_of_partitions}, '
            f'number of rounds: {self.number_of_rounds})'
        )


class Generator:
    def __init__(self, configs, testcases_per_file=100, folder_path='./'):
        """ Instantiate the generator.

        Generate indices of nodes. There are three kinds of nodes:
        (1) Target nodes: Represented by 'f', these are the nodes for which
            we will create Twins, to emulate byzantine behavior.
        (2) Honest nodes: These are the honest nodes
        (3) Twin nodes: These are the twins of target nodes (see 1 above)

        Below, we generate indices using the ordering convention:
        target_nodes, honest_nodes, twin_nodes
        |----------------------------------------------------------------------|
        |    0..f-1    |  f..NUM_OF_NODES-1   | NUM_OF_NODES..NUM_OF_NODES+f-1 |
        |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|
        | target_nodes |    honest_nodes      |           twin_nodes           |
        |----------------------------------------------------------------------|

        Args:
            configs (Configs): The generator configs.
            testcases_per_file (int, optional): The maximum number of testcases
                to print in a single file. Defaults to 100.
            folder_path (str, optional): The output directory where to print
                the testcases. Defaults to './'.

        Raises:
            GeneratorError: Raised upon invalid input arguments.
        """
        self.logger = logging.getLogger(name='generator')
        ok = isinstance(configs, Configs)
        ok &= isinstance(testcases_per_file, int)
        ok &= testcases_per_file > 0
        ok &= isinstance(folder_path, str)
        if not ok:
            raise GeneratorError('Bad input arguments.')

        self.configs = configs
        self.testcases_per_file = testcases_per_file
        self.folder_path = folder_path

        self.f = (self.configs.number_of_nodes - 1) // 3
        self.nodes = [x for x in range(self.configs.number_of_nodes+self.f)]

        if len(self.nodes) < self.configs.number_of_partitions:
            raise GeneratorError(
                'There should be at least as many nodes as partitions. '
                f'Input: {len(self.nodes)} nodes and '
                f'{self.configs.number_of_partitions} partitions.'
            )

        self.logger.info(
            f'''Generator successfully instantiated with the following settings:
            \t configs: {str(self.configs)}
            \t maximum testcases per file: {self.testcases_per_file}
            \t output directory: {self.folder_path}'''
        )

    @property
    def target_nodes(self):
        """ The list of nodes that have a twin.

        Returns:
            list(int): A list of nodes' indeces.
        """
        return self.nodes[:self.f]

    @property
    def honest_nodes(self):
        """ The list of nodes that do not have a twin.

        Returns:
            list(int): A list of nodes' indeces.
        """
        return self.nodes[self.f:self.configs.number_of_nodes]

    @property
    def twin_nodes(self):
        """ The list of nodes that are twins of  `target_nodes`.

        Returns:
            list(int): A list of nodes' indeces.
        """
        return self.nodes[self.configs.number_of_nodes:]

    @property
    def testcases_length(self):
        """ Forecast the total number of testcases.

        Returns:
            int: The total number of testcases.
        """
        total = self.S(len(self.nodes), self.configs.number_of_partitions)
        total *= len(self.target_nodes)
        total **= self.configs.number_of_rounds
        return total

    def get_twin(self, node):
        """ Get the twin of a specific node.

        Args:
            node (int): The index of the node for which to return the twin.

        Returns:
            int: A node's index.
        """
        assert node in self.target_nodes
        return self.nodes[self.configs.number_of_nodes+node]

    def S(self, n, k):
        """ Compute the Stirling numbers of the second kind.

        Args:
            n (int): Number of objects.
            k (int): Number of non-empty subsets.

        Returns:
            int: The Stirling numbers of the second kind.
        """
        assert isinstance(n, int) and isinstance(k, int)
        assert n > 0 and k > 0 and n >= k
        S = [(-1)**i * (f(k)//f(i)//f(k - i)) * (k-i)**n for i in range(k+1)]
        return sum(S) // f(k)

    def make_partitions(self):
        """ Find all possible ways in which n nodes can be partitioned into k
        partitions.

        This problems is known as "Stirling Number of the Second Kind".
        "In combinatorics, the Stirling numbers of the second kind tell
        us how many ways there are of dividing up a set of n objects
        (all different, or at least all labeled) into k nonempty subsets."

        E.g. for n={0,1,2} and k=2, possible partition are:
        [   [ [0,1], [2] ],
            [ [0,2], [1] ],
            [ [1,2], [0] ],
            [ [2], [0,1] ], etc.
        ]

        Returns:
            list: All possible partitions.
        """
        def stirling2(n, k):
            """ Provies all solutions of the Stirling Number of the Second Kind.

            Args:
                n (int): The number of objects.
                k (int): The number of sets.

            Returns:
                list: All solutions of the Stirling number of the second kind.
            """
            assert n > 0 and k > 0
            if k == 1:
                return [[[x for x in range(n)]]]
            elif k == n:
                return [[[x] for x in range(n)]]
            else:
                s_n1_k1 = stirling2(n-1, k-1)
                for i in range(len(s_n1_k1)):
                    s_n1_k1[i].append([n-1])

                tmp = stirling2(n-1, k)
                k_s_n1_k = []
                for _ in range(k):
                    k_s_n1_k += deepcopy(tmp)
                for i in range(len(tmp)*k):
                    k_s_n1_k[i][i // len(tmp)] += [n-1]

                return s_n1_k1 + k_s_n1_k

        return stirling2(len(self.nodes), self.configs.number_of_partitions)

    def combine_partitions_with_leaders(self, partitions):
        """ Assign leaders to partitions.

        Args:
            partitions (list): List of all partitions.

        Yields:
            tuple: A tuple of (leader, partition)
        """
        for partition in partitions:
            for leader in self.target_nodes:
                yield (leader, partition)

    def combine_scenarios_with_rounds(self, scenarios):
        """ Combine the input parition-leader scenarios with rounds.

        Args:
            tuple: An iterator containing tuples of (leader, partition).

        Returns:
            list: an iterator of testcases.
        """
        return product(scenarios, repeat=self.configs.number_of_rounds)

    def print(self, index, testcases, dryrun=False, filter=None):
        if dryrun:
            self.logger.info('Dry-run enabled: no files will be created.')

        num_of_chunks = ceil(self.testcases_length / self.testcases_per_file)
        chunks = ichunked(testcases, num_of_chunks)
        for i, chunk in enumerate(chunks):
            filename = f'tmp-{index}' if dryrun else f'testcase-{index}-{i}'
            with open(join(self.folder_path, filename), 'w') as f:
                for testcase in chunk:
                    if filter is not None and not filter(testcase):
                        continue

                    twins_round_proposers_idx, round_partitions_idx = {}, {}
                    for round_number, scenario in enumerate(testcase):
                        leader, partition = scenario
                        leaders = [leader]
                        if leader in self.target_nodes:
                            leaders.append(self.get_twin(leader))
                        twins_round_proposers_idx[round_number] = leaders
                        round_partitions_idx[round_number] = partition

                    f.write(
                        f'''{self.configs.number_of_rounds}
                        {self.configs.number_of_nodes}
                        {self.configs.number_of_partitions}
                        {twins_round_proposers_idx}
                        {round_partitions_idx}'''
                    )

    def run(self, dryrun=False, filter=None, number_of_workers=1):
        self.logger.info(
            f'Generating {self.testcases_length} testcases...'
        )

        # Make partitions
        partitions = self.make_partitions()

        # Combine partitions with leaders
        scenarios = self.combine_partitions_with_leaders(partitions)

        # Combine the parition-leader scenarios from above with rounds
        testcases = self.combine_scenarios_with_rounds(scenarios)

        # Print the resulting testcases to files
        from more_itertools import distribute
        threads = []
        chunks = distribute(number_of_workers, testcases)
        for i in range(number_of_workers):
            t = Thread(
                target=self.print, args=(i, chunks[i], dryrun, filter)
            )
            t.start()
            threads.append(t)
        [t.join() for t in threads]

        #self.print(0, testcases, dryrun=dryrun, filter=filter)
        self.logger.info(f'Finished.')

        '''
        TODO:  1 Finish comments
               2 Support multiple threads on a single machine
               3 Support multiple machines (use itertool.islice)
               4 100% test coverage (find a way to moch 'open' and 'f.write')
        '''
