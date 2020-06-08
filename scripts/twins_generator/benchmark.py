from generator import Generator
from datetime import timedelta
import time

generator = Generator(4, 2, 5, testcases_per_file=100)
print(f'Generating {generator.testcases_length} testcases..')
start_time = time.perf_counter()
generator.run(dryrun=True, workers=8)
elapsed_time = time.perf_counter() - start_time
print(f'Elapsed time: {str(timedelta(seconds=elapsed_time))}')
