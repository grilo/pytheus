#!/usr/bin/env python

"""
    This module is pure syntatic sugar, there's no actual functionality.
    You decorate any function with the type of metric you want to collect,
    passing on to the decorator itself any relevant data regarding that
    specific metric.
"""

import pytheus.meter
import pytheus.collector


def metric_decorator(metric):
    def real_decorator(function):
        pytheus.collector.Base.register(metric, function)
        return function
    return real_decorator


def gauge(name, description=None):
    return metric_decorator(pytheus.meter.Gauge(name, description))

def counter(name, description=None):
    return metric_decorator(pytheus.meter.Counter(name, description))

def summary(name, buckets, description=None):
    return metric_decorator(pytheus.meter.Summary(name, buckets, description))

def histogram(name, buckets, description=None):
    return metric_decorator(pytheus.meter.Histogram(name, buckets, description))
