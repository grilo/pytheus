#!/usr/bin/env python

import pytest

import protean.meter


def test_gauge(mocker):
    with mocker.patch('time.time', return_value=407424600):

        g = protean.meter.Gauge('metric_name', "this metric's description")
        g.set(1.0, hello='world', another_label='somethingelse')
        g.set(2.0, xpto='blah', another_label='somethingelse')
        g.set(3.0, somethingelse='entirely')

        expected = [
            "# HELP metric_name this metric's description",
            "# TYPE metric_name gauge",
            'metric_name{another_label="somethingelse",hello="world"} 1.0',
            'metric_name{another_label="somethingelse",xpto="blah"} 2.0',
            'metric_name{somethingelse="entirely"} 3.0',
        ]

        out = g.to_string().splitlines()
        for line in expected:
            assert line == out.pop(0)

def test_counter(mocker):

    with mocker.patch('time.time', return_value=407424600):
        c = protean.meter.Counter('metric_name', "this metric's description")
        c.inc(hello='world', another_label='somethingelse')
        c.inc(2.0, hello='world', another_label='somethingelse')
        c.inc(5.0, random='label')

        expected = [
            "# HELP metric_name this metric's description",
            "# TYPE metric_name counter",
            'metric_name{another_label="somethingelse",hello="world"} 3.0',
            'metric_name{random="label"} 5.0',
        ]

        out = c.to_string().splitlines()
        for line in expected:
            assert line == out.pop(0)

def test_summary():
    buckets = [0.1, 0.5, 1.0]
    s = protean.meter.Summary("metric_name",
                                buckets,
                                "this metric's description")
    s.observe(0.001, hello='world', moarlabel='blah')
    s.observe(0.2, hello='world', moarlabel='blah')
    s.observe(0.3, hello='world', moarlabel='blah')
    s.observe(0.6, hello='world', moarlabel='blah')
    s.observe(2.0, hello='world', moarlabel='blah')
    s.observe(0.3, differentlabel='samebucket')
    s.observe(0.6, differentlabel='samebucket')

    expected = [
        "# HELP metric_name this metric's description",
        "# TYPE metric_name summary",
        'metric_name{hello="world",moarlabel="blah",quantile="0.1"} 0.201',
        'metric_name{hello="world",moarlabel="blah",quantile="0.5"} 0.9',
        'metric_name{hello="world",moarlabel="blah",quantile="1.0"} 2.0',
        'metric_name_sum{hello="world",moarlabel="blah"} 3.101',
        'metric_name_count{hello="world",moarlabel="blah"} 5',
        'metric_name{differentlabel="samebucket",quantile="0.1"} 0.0',
        'metric_name{differentlabel="samebucket",quantile="0.5"} 0.3',
        'metric_name{differentlabel="samebucket",quantile="1.0"} 0.6',
        'metric_name_sum{differentlabel="samebucket"} 0.9',
        'metric_name_count{differentlabel="samebucket"} 2',
    ]

    out = s.to_string().splitlines()
    for line in expected:
        assert line == out.pop(0)


def test_histogram():
    buckets = [1, 10, 20]
    h = protean.meter.Histogram("metric_name",
                                buckets,
                                "this metric's description")
    h.observe(0.001, hello='world', moarlabel='blah')
    h.observe(10, hello='world', moarlabel='blah')
    h.observe(11, hello='world', moarlabel='blah')
    h.observe(15, hello='world', moarlabel='blah')
    h.observe(30, hello='world', moarlabel='blah')
    h.observe(0.3, differentlabel='samebucket')
    h.observe(0.6, differentlabel='samebucket')

    expected = [
        "# HELP metric_name this metric's description",
        "# TYPE metric_name histogram",
        'metric_name_bucket{hello="world",moarlabel="blah",le="1"} 0.001',
        'metric_name_bucket{hello="world",moarlabel="blah",le="10"} 10.001',
        'metric_name_bucket{hello="world",moarlabel="blah",le="20"} 36.001',
        'metric_name_bucket{hello="world",moarlabel="blah",le="+Inf"} 4',
        'metric_name_sum{hello="world",moarlabel="blah"} 36.001',
        'metric_name_count{hello="world",moarlabel="blah"} 4',
        'metric_name_bucket{differentlabel="samebucket",le="1"} 0.9',
        'metric_name_bucket{differentlabel="samebucket",le="10"} 0.9',
        'metric_name_bucket{differentlabel="samebucket",le="20"} 0.9',
        'metric_name_bucket{differentlabel="samebucket",le="+Inf"} 2',
        'metric_name_sum{differentlabel="samebucket"} 0.9',
        'metric_name_count{differentlabel="samebucket"} 2',
    ]

    out = h.to_string().splitlines()
    for line in expected:
        assert line == out.pop(0)
