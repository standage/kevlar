#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2017 The Regents of the University of California
#
# This file is part of kevlar (http://github.com/dib-lab/kevlar) and is
# licensed under the MIT license: see LICENSE.
# -----------------------------------------------------------------------------

import glob
import pytest
import sys
import khmer
import kevlar
from kevlar.seqio import AnnotatedReadSet


@pytest.fixture
def bogusrefr():
    mask = khmer.Nodetable(13, 1e7 / 4, 4)
    maskfile = kevlar.tests.data_file('bogus-genome/refr.fa')
    mask.consume_seqfile(maskfile)
    return mask


@pytest.fixture
def bogusrefrcontam():
    mask = khmer.Nodetable(13, 1e7 / 4, 4)
    mask.consume_seqfile(kevlar.tests.data_file('bogus-genome/refr.fa'))
    mask.consume_seqfile(kevlar.tests.data_file('bogus-genome/contam1.fa'))
    return mask


@pytest.fixture
def ctrl3():
    augfastq = kevlar.tests.data_file('trio1/novel_3_1,2.txt')
    readset = AnnotatedReadSet(13, 1e7)
    for record in kevlar.parse_augmented_fastx(kevlar.open(augfastq, 'r')):
        readset.add(record)
    return readset


def test_load_mask():
    infile = kevlar.tests.data_file('bogus-genome/refr.fa')
    mask = kevlar.filter.load_mask([infile], 25, 1e7)
    assert mask.get('GGCCCCGAACTAGGGGGCCTACGTT') > 0
    assert mask.get('GCTGGCTAAATTTTCATACTAACTA') > 0
    assert mask.get('G' * 25) == 0


def test_load_mask_multi_file():
    infiles = [
        kevlar.tests.data_file('bogus-genome/refr.fa'),
        kevlar.tests.data_file('bogus-genome/contam1.fa')
    ]
    mask = kevlar.filter.load_mask(infiles, 25, 1e7)
    assert mask.get('GGCCCCGAACTAGGGGGCCTACGTT') > 0  # reference
    assert mask.get('GCTGGCTAAATTTTCATACTAACTA') > 0  # reference
    assert mask.get('AATGTAGGTAGTTTTGTGCACAGTT') > 0  # contam
    assert mask.get('TCGCGCGCGTCCAAGTCGAGACCGC') > 0  # contam
    assert mask.get('G' * 25) == 0


def test_load_readset():
    filelist = kevlar.tests.data_glob('collect.beta.?.txt')
    readset = AnnotatedReadSet(19, 1e3)
    for record in kevlar.seqio.afxstream(filelist):
        readset.add(record)

    assert len(readset) == 8
    assert readset
    kmers = [
        'AGGGGCGTGACTTAATAAG', 'GGGCGTGACTTAATAAGGT',
        'TAGGGGCGTGACTTAATAA', 'GGGGCGTGACTTAATAAGG',
    ]
    for kmer in kmers:
        assert readset._counts.get(kmer) == 8


def test_validate():
    filelist = kevlar.tests.data_glob('collect.alpha.txt')
    readset = AnnotatedReadSet(19, 5e3)
    for record in kevlar.seqio.afxstream(filelist):
        readset.add(record)
    readset.validate()

    assert readset.valid == (4, 32)
    assert len(readset) == 9
    assert readset.discarded == 1

    badkmers = ['CAGGCCAGGGATCGCCGTG']
    goodkmers = [
        'AGGGGCGTGACTTAATAAG', 'GGGCGTGACTTAATAAGGT',
        'TAGGGGCGTGACTTAATAA', 'GGGGCGTGACTTAATAAGG',
    ]
    for record in readset:
        for kmer in record.ikmers:
            assert kmer.sequence not in badkmers and \
                kevlar.revcom(kmer.sequence) not in badkmers
            assert kmer.sequence in goodkmers or \
                kevlar.revcom(kmer.sequence) in goodkmers


def test_validate_minabund():
    filelist = kevlar.tests.data_glob('collect.beta.?.txt')
    readset = AnnotatedReadSet(19, 5e3)
    for record in kevlar.seqio.afxstream(filelist):
        readset.add(record)
    readset.validate()
    assert readset.valid == (4, 32)

    readset = AnnotatedReadSet(19, 5e3)
    for record in kevlar.seqio.afxstream(filelist):
        readset.add(record)
    readset.validate(minabund=9)
    assert readset.valid == (0, 0)


def test_validate_with_mask():
    kmer = 'AGGGGCGTGACTTAATAAG'
    mask = khmer.Nodetable(19, 1e3, 2)
    mask.add(kmer)

    filelist = kevlar.tests.data_glob('collect.beta.?.txt')
    readset = AnnotatedReadSet(19, 5e3)
    for record in kevlar.seqio.afxstream(filelist):
        readset.add(record)
    readset.validate(mask=mask)
    assert readset.valid == (3, 24)
    for record in readset:
        for ikmer in record.ikmers:
            assert ikmer.sequence != kmer
            assert kevlar.revcom(ikmer.sequence) != kmer


def test_ctrl3(ctrl3):
    readset = ctrl3
    readset.validate(minabund=6)
    assert readset.valid == (424, 5782)


def test_ctrl3_refr(ctrl3, bogusrefr):
    readset = ctrl3
    readset.validate(mask=bogusrefr, minabund=6)
    assert readset.valid == (424, 5782)


def test_ctrl3_refr_contam(ctrl3, bogusrefrcontam):
    readset = ctrl3
    readset.validate(mask=bogusrefrcontam, minabund=6)
    assert readset.valid == (13, 171)


def test_filter_main(capsys):
    arglist = [
        'filter',
        '--mask',
        kevlar.tests.data_file('bogus-genome/refr.fa'),
        kevlar.tests.data_file('bogus-genome/contam1.fa'),
        '--mask-memory', '10M',
        '--mask-max-fpr', '0.001',
        '--abund-memory', '10M',
        '--abund-max-fpr', '0.001',
        '--min-abund', '6',
        '--ksize', '13',
        kevlar.tests.data_file('trio1/novel_3_1,2.txt'),
    ]
    args = kevlar.cli.parser().parse_args(arglist)
    kevlar.filter.main(args)

    out, err = capsys.readouterr()
    assert '171 instances of 13 distinct k-mers validated as novel' in err
