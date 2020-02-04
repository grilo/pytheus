
#!/usr/bin/env python

import time
import collections
import re


class InvalidLabelError(Exception):
    """When the label is incorrectly formatted."""
    pass

class InvalidQuantileError(Exception):
    """When the buckets for a Summary exceed 1."""
    pass


class SimpleMetric(object):

    @staticmethod
    def _validate_labels(labels):
        """According to the docs:
            Label names may contain ASCII letters, numbers, as well as underscores.
            They must match the regex [a-zA-Z_][a-zA-Z0-9_]*.
            Label names beginning with __ are reserved for internal use.
        """
        for label in labels:
            if not re.match('[a-zA-Z_][a-zA-Z0-9_]*.', label):
                raise InvalidLabelError("Doesn't match the regex: %s" % (label))

    def __init__(self, name, value="NaN", labels=None, timestamp=False):
        self.name = name
        self.value = value
        if labels is None:
            labels = {}
        self.labels = labels
        self.timestamp = timestamp
        SimpleMetric._validate_labels(self.labels)

    def to_string(self):
        out = "{0}".format(self.name)
        if self.labels:
            labels = ['{0}="{1}"'.format(str(k), str(v)) for k, v in self.labels.items()]
            out += "{{{labels}}}".format(labels=','.join(labels))
        out += " {value}".format(value=self.value)
        if self.timestamp:
            out += " {0}".format(str(int(time.time()))) # timestamp
        return out + "\n"


class QuantileBucket(object):

    @staticmethod
    def _validate_buckets(buckets):
        if max(buckets) > 1:
            raise InvalidQuantileError("Summary buckets shouldn't exceed value 1 (0 < Q < 1).")

    def __init__(self, name, buckets, labels):
        self.name = name
        self.buckets = dict.fromkeys(buckets, 0.0)
        self.labels = labels
        self.values = []
        QuantileBucket._validate_buckets(self.buckets)

    def add(self, value):
        self.values.append(value)

    def to_string(self):
        out = ""
        maximum = max(self.values)
        self.values = sorted(self.values)

        # Organize all values into their buckets
        for value in self.values:
            percentile = float(value) * 100 / maximum / 100
            for quantile in sorted(self.buckets):
                if percentile <= quantile:
                    self.buckets[quantile] += value
                    break

        for quantile in sorted(self.buckets):
            value = self.buckets[quantile]
            labels = collections.OrderedDict(self.labels, quantile=quantile)
            out += SimpleMetric(self.name, value, labels).to_string()
        out += SimpleMetric(self.name + "_sum", sum(self.values), self.labels).to_string()
        out += SimpleMetric(self.name + "_count", len(self.values), self.labels).to_string()
        return out


class LessOrEqualBucket(object):

    def __init__(self, name, buckets, labels):
        self.name = name
        self.buckets = dict.fromkeys(buckets, 0.0)
        self.labels = labels
        self.count = 0
        self.sum = 0

    def add(self, value):

        added = False
        for bucket in sorted(self.buckets):
            # Histograms are cummulative. We add the value to all possible
            # buckets.
            if value <= bucket:
                self.buckets[bucket] += value
                added = True

        if added:
            self.count += 1
            self.sum += value

    def to_string(self):
        out = ""
        for quantile in sorted(self.buckets.keys()):
            value = self.buckets[quantile]
            labels = collections.OrderedDict(self.labels)
            labels.update({'le': quantile}) # LE means less or equal
            out += SimpleMetric(self.name + "_bucket", value, labels).to_string()
        labels = collections.OrderedDict(self.labels)
        labels.update({'le': '+Inf'})
        out += SimpleMetric(self.name + "_bucket", self.count, labels).to_string()
        out += SimpleMetric(self.name + "_sum", self.sum, self.labels).to_string()
        out += SimpleMetric(self.name + "_count", self.count, self.labels).to_string()
        return out


class Base(object):

    def __init__(self, name, description=None):
        if not description:
            description = name

        self.name = name
        self.description = description
        self.metric_type = None

    def _encode(self, labels):
        encoded = ','.join(["{0}={1}".format(k, v) for k, v in labels.items()])
        if not encoded:
            encoded = ''
        return encoded

    def _sorted_dict(self, unordered):
        """
            Take a normal dictionary and returns a OrderedDict.
            Ensures that the data being exposed (with to_string) is always
            returned in the same order.
            Not sure if this is a true requirement for Prometheus to
            correctly scrape our stuff, but it does make the output look
            alot more consistent.
        """
        sorted_dict = collections.OrderedDict()
        for key in sorted(unordered.keys()):
            sorted_dict[key] = unordered[key]
        return sorted_dict

    def _help(self):
        return "# HELP {name} {desc}".format(name=self.name, desc=self.description)

    def _type(self):
        return "# TYPE {name} {metric_type}".format(
            name=self.name,
            metric_type=self.__class__.__name__.lower()
        )

    def to_string(self):
        out = self._help() + "\n"
        out += self._type() + "\n"
        return out


class Gauge(Base):

    def __init__(self, name, description=None):
        super(Gauge, self).__init__(name, description)
        self.label_metric = collections.OrderedDict()

    def set(self, value, **labels):
        labels = self._sorted_dict(labels)
        key = self._encode(labels)
        self.label_metric[key] = SimpleMetric(self.name, value, labels)

    def measure(self, value, **labels):
        self.set(value, **labels)
        return self

    def to_string(self):
        out = super(Gauge, self).to_string()
        for metric in self.label_metric.values():
            out += metric.to_string()
        return out


class Counter(Gauge):

    def inc(self, amount=1.0, **labels):
        labels = self._sorted_dict(labels)
        key = self._encode(labels)
        if key not in self.label_metric:
            self.set(0.0, **labels)
        self.label_metric[key].value += float(amount)

    def measure(self, value, **labels):
        self.inc(value, **labels)
        return self


class Summary(Base):
    """
        Summaries provide distribution between 0 < X < 1
        When determining the buckets for summary, they should
        all be a value which complies with the forecasted
        distribution.
            correct: [0.001, 0.1, 0.2, 0.5, 1.0]
            incorrect: [10, 15, 20]
        If the "incorrect" example is what you're looking for, use a histogram.
    """

    def __init__(self, name, buckets, description=None):
        super(Summary, self).__init__(name, description)
        self.buckets = sorted(buckets)
        self.label_bucket = collections.OrderedDict()

    def observe(self, value, **labels):
        labels = self._sorted_dict(labels)
        key = self._encode(labels)
        if not key in self.label_bucket:
            self.label_bucket[key] = QuantileBucket(self.name, self.buckets, labels)
        return self.label_bucket[key].add(value)

    def measure(self, value, **labels):
        self.observe(value, **labels)
        return self

    def to_string(self):
        out = super(Summary, self).to_string()
        for bucket in self.label_bucket.values():
            out += bucket.to_string()
        return out


class Histogram(Summary):
    """
        Histograms are be cumulative, unlike summaries
        In a bucket of [10, 20, 30]
        If an observed event is "15" and another with "25",
        it should show:
            10: 0
            20: 1
            30: 2
    """

    def observe(self, value, **labels):
        labels = self._sorted_dict(labels)
        key = self._encode(labels)
        if not key in self.label_bucket:
            self.label_bucket[key] = LessOrEqualBucket(self.name, self.buckets, labels)
        return self.label_bucket[key].add(value)

    def measure(self, value, **labels):
        self.observe(value, **labels)
        return self
