#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2019 Battelle National Biodefense Institute
#
# This file is part of kevlar (http://github.com/dib-lab/kevlar) and is
# licensed under the MIT license: see LICENSE.
# -----------------------------------------------------------------------------


def subparser(subparsers):
    """Define the `kevlar varfilter` command-line interface."""

    subparser = subparsers.add_parser(
        'varfilter', description='Filter out variants falling in the genomic '
        'regions specified by the BED file(s). This can be used to exclude '
        'putative variant calls corresponding to common variants, segmental '
        'duplications, or other problematic loci.'
    )

    subparser.add_argument(
        '-o', '--out', metavar='FILE', help='file to which filtered variants '
        'will be written; default is terminal (standard output)'
    )
    subparser.add_argument(
        '--load-index', action='store_true', help='the "filt" argument is a '
        'pre-loaded index, not a BED file'
    )
    subparser.add_argument(
        '--save-index', metavar='FILE', help='save the index to "FILE" once '
        'loaded'
    )
    subparser.add_argument(
        'filt', help='BED file (or pre-loaded index) containing regions to '
        'filter out'
    )
    subparser.add_argument(
        'vcf', nargs='+', help='VCF file(s) with calls to filter'
    )
