#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2016 The Regents of the University of California
#
# This file is part of kevlar (http://github.com/dib-lab/kevlar) and is
# licensed under the MIT license: see LICENSE.
# -----------------------------------------------------------------------------

import khmer
from khmer import khmer_args


def subparser(subparsers):
    """Define the `kevlar dist` command-line interface."""

    desc = 'Compute the k-mer abundance distribution for a data set.'

    subparser = subparsers.add_parser('dist', description=desc)
    subparser.add_argument('-o', '--out', metavar='FILE', help='output file; '
                           'default is terminal (stdout)')
    subparser.add_argument('-k', '--ksize', metavar='K', help='k-mer size')
    subparser.add_argument('-M', '--memory', type=khmer_args.memory_setting,
                           default=1e6, metavar='MEM',
                           help='memory to allocate for k-mer counting')
    subparser.add_argument('-t', '--threads', type=int, metavar='T', default=1,
                           help='number of threads to use for k-mer counting; '
                           'default is 1')
    subparser.add_argument('-p', '--plot', metavar='PNG', help='plot k-mer '
                           'abundance distribution to file `PNG`')
    subparser.add_argument('mask', help='nodetable containing target k-mers '
                           'to count (such as single-copy exonic k-mers)')
    subparser.add_argument('infiles', nargs='+', help='input files in '
                           'FASTA/FASTQ format')
