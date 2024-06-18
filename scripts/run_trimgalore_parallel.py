import os
import argparse
import subprocess
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

def ensure_dir_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def run_trimgalore_sample(sample, input_dir, output_dir, threads, length, quality):
    trimgalore_output_dir = os.path.join(output_dir, 'TrimGalore')
    ensure_dir_exists(trimgalore_output_dir)

    r1_path = os.path.join(input_dir, sample[0])
    r2_path = os.path.join(input_dir, sample[1])
    cmd = [
        'trim_galore',
        '--paired',
        '--fastqc',
        '--quality', str(quality),
        '--length', str(length),
        '--adapter', 'AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC',
        '--adapter2', 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT',
        '--cores', str(threads),
        '--output_dir', trimgalore_output_dir,
        r1_path, r2_path
    ]
    subprocess.run(cmd, check=True)

def run_trimgalore(input_dir, output_dir, total_threads, length, quality):
    fastq_files = [f for f in os.listdir(input_dir) if f.endswith('.fastq.gz')]
    fastq_pairs = {}

    for fastq_file in fastq_files:
        if '_R1.fastq.gz' in fastq_file:
            base_name = fastq_file.replace('_R1.fastq.gz', '')
            if base_name in fastq_pairs:
                fastq_pairs[base_name][0] = fastq_file
            else:
                fastq_pairs[base_name] = [fastq_file, None]
        elif '_R2.fastq.gz' in fastq_file:
            base_name = fastq_file.replace('_R2.fastq.gz', '')
            if base_name in fastq_pairs:
                fastq_pairs[base_name][1] = fastq_file
            else:
                fastq_pairs[base_name] = [None, fastq_file]

    paired_samples = [pair for pair in fastq_pairs.values() if None not in pair]
    num_samples = len(paired_samples)
    print('Number of paired-end sample: ' + str(num_samples))
    threads_per_sample = min(max(total_threads // num_samples, 4), 8)
    print('Threads per sample: ' + str(threads_per_sample))

    with ThreadPoolExecutor(max_workers=num_samples) as executor:
        futures = [
            executor.submit(run_trimgalore_sample, sample, input_dir, output_dir, threads_per_sample, length, quality)
            for sample in paired_samples
        ]
        for future in futures:
            future.result()  # to re-raise exceptions if any

def main():
    parser = argparse.ArgumentParser(description='Run TrimGalore on FASTQ files.')
    parser.add_argument('-i', '--input_dir', required=True, help='Directory containing input FASTQ files.')
    parser.add_argument('-o', '--output_dir', required=True, help='Directory to store output files.')
    parser.add_argument('-t', '--threads', type=int, default=multiprocessing.cpu_count(), help='Total number of threads available.')
    parser.add_argument('--length', type=int, default=40, help='Minimum paired-end read length to allow retention. Default is 40')
    parser.add_argument('--quality', type=int, default=20, help='Trim low-quality ends from reads in addition to adapter removal. Default is 20.')
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)

    ensure_dir_exists(output_dir)
    
    run_trimgalore(input_dir, output_dir, args.threads, args.length, args.quality)

if __name__ == "__main__":
    main()

