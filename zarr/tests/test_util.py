# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division


import numpy as np
from nose.tools import (eq_ as eq, assert_raises, assert_true, assert_false, assert_is_instance)


from zarr.util import (normalize_shape, normalize_chunks, is_total_slice, normalize_resize_args,
                       human_readable_size, normalize_order, guess_chunks, info_html_report,
                       info_text_report, normalize_fill_value)


def test_normalize_shape():
    eq((100,), normalize_shape((100,)))
    eq((100,), normalize_shape([100]))
    eq((100,), normalize_shape(100))
    with assert_raises(TypeError):
        normalize_shape(None)
    with assert_raises(ValueError):
        normalize_shape('foo')


def test_normalize_chunks():
    eq((10,), normalize_chunks((10,), (100,), 1))
    eq((10,), normalize_chunks([10], (100,), 1))
    eq((10,), normalize_chunks(10, (100,), 1))
    eq((10, 10), normalize_chunks((10, 10), (100, 10), 1))
    eq((10, 10), normalize_chunks(10, (100, 10), 1))
    eq((10, 10), normalize_chunks((10, None), (100, 10), 1))
    eq((30, 20, 10), normalize_chunks(30, (100, 20, 10), 1))
    eq((30, 20, 10), normalize_chunks((30,), (100, 20, 10), 1))
    eq((30, 20, 10), normalize_chunks((30, None), (100, 20, 10), 1))
    eq((30, 20, 10), normalize_chunks((30, None, None), (100, 20, 10), 1))
    eq((30, 20, 10), normalize_chunks((30, 20, None), (100, 20, 10), 1))
    eq((30, 20, 10), normalize_chunks((30, 20, 10), (100, 20, 10), 1))
    with assert_raises(ValueError):
        normalize_chunks('foo', (100,), 1)
    with assert_raises(ValueError):
        normalize_chunks((100, 10), (100,), 1)

    # test auto-chunking
    chunks = normalize_chunks(None, (100,), 1)
    eq((100,), chunks)


def test_is_total_slice():

    # 1D
    assert_true(is_total_slice(Ellipsis, (100,)))
    assert_true(is_total_slice(slice(None), (100,)))
    assert_true(is_total_slice(slice(0, 100), (100,)))
    assert_false(is_total_slice(slice(0, 50), (100,)))
    assert_false(is_total_slice(slice(0, 100, 2), (100,)))

    # 2D
    assert_true(is_total_slice(Ellipsis, (100, 100)))
    assert_true(is_total_slice(slice(None), (100, 100)))
    assert_true(is_total_slice((slice(None), slice(None)), (100, 100)))
    assert_true(is_total_slice((slice(0, 100), slice(0, 100)), (100, 100)))
    assert_false(is_total_slice((slice(0, 100), slice(0, 50)), (100, 100)))
    assert_false(is_total_slice((slice(0, 50), slice(0, 100)), (100, 100)))
    assert_false(is_total_slice((slice(0, 50), slice(0, 50)), (100, 100)))
    assert_false(is_total_slice((slice(0, 100, 2), slice(0, 100)), (100, 100)))

    with assert_raises(TypeError):
        is_total_slice('foo', (100,))


def test_normalize_resize_args():

    # 1D
    eq((200,), normalize_resize_args((100,), 200))
    eq((200,), normalize_resize_args((100,), (200,)))

    # 2D
    eq((200, 100), normalize_resize_args((100, 100), (200, 100)))
    eq((200, 100), normalize_resize_args((100, 100), (200, None)))
    eq((200, 100), normalize_resize_args((100, 100), 200, 100))
    eq((200, 100), normalize_resize_args((100, 100), 200, None))

    with assert_raises(ValueError):
        normalize_resize_args((100,), (200, 100))


def test_human_readable_size():
    eq('100', human_readable_size(100))
    eq('1.0K', human_readable_size(2**10))
    eq('1.0M', human_readable_size(2**20))
    eq('1.0G', human_readable_size(2**30))
    eq('1.0T', human_readable_size(2**40))
    eq('1.0P', human_readable_size(2**50))


def test_normalize_order():
    eq('F', normalize_order('F'))
    eq('C', normalize_order('C'))
    eq('F', normalize_order('f'))
    eq('C', normalize_order('c'))
    with assert_raises(ValueError):
        normalize_order('foo')


def test_normalize_fill_value():
    eq(b'', normalize_fill_value(0, dtype=np.dtype('S1')))
    eq(b'', normalize_fill_value(0, dtype=np.dtype([('foo', 'i4'), ('bar', 'f8')])))
    eq('', normalize_fill_value(0, dtype=np.dtype('U1')))


def test_guess_chunks():
    shapes = (
        (100,),
        (100, 100),
        (1000000,),
        (1000000000,),
        (10000000000000000000000,),
        (10000, 10000),
        (10000000, 1000),
        (1000, 10000000),
        (10000000, 1000, 2),
        (1000, 10000000, 2),
        (10000, 10000, 10000),
        (100000, 100000, 100000),
        (1000000000, 1000000000, 1000000000),
        (0,),
        (0, 0),
        (10, 0),
        (0, 10),
        (1, 2, 0, 4, 5),
    )
    for shape in shapes:
        chunks = guess_chunks(shape, 1)
        assert_is_instance(chunks, tuple)
        eq(len(chunks), len(shape))
        # doesn't make any sense to allow chunks to have zero length dimension
        assert all([0 < c <= max(s, 1) for c, s in zip(chunks, shape)])

    # ludicrous itemsize
    chunks = guess_chunks((1000000,), 40000000000)
    assert_is_instance(chunks, tuple)
    eq((1,), chunks)


def test_info_text_report():
    items = [('foo', 'bar'), ('baz', 'qux')]
    expect = "foo : bar\nbaz : qux\n"
    eq(expect, info_text_report(items))


def test_info_html_report():
    items = [('foo', 'bar'), ('baz', 'qux')]
    actual = info_html_report(items)
    eq('<table', actual[:6])
    eq('</table>', actual[-8:])
