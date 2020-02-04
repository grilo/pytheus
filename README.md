Pytheus

An exporter for metrics compatible with Prometheus scraping.

See: https://prometheus.io/

## Usage

```python

import pytheus

from pytheus.decorators import *

@counter('a_special_counter', 'a description')
def something(*args):
    # Run your collection code here
    return "10"

pytheus.start()
```

What this will do is:
  - Create a metric of type `Counter` with name "a_special_counter".
  - Increment it by 10 every time the `something` function is executed.
  - Expose the collected metric in prometheus format (default port: 5000).

See: https://prometheus.io/docs/concepts/metric_types/

If you point your prometheus service to the service, it should start
scraping them.

Under normal circumstances, you'll want `something` to be meaningful. For
instance, you may want to run an http request, or parse some unconventional
log files.

## Implementation

It's using https://github.com/grilo/hollywood which enables concurrent scraping.

The actual implementation of the metrics can be found in `pytheus/meter.py` and
contains the bulk of the logic. The rest is just syntatic sugar and a bare bones
http request handler.

## Features/limitations

Implemented in python2.7, not tested in >=3.

This is not very tested, and was done mostly as a learning project to grasp
prometheus metrics. The API is pretty nice, but it lacks many of the official
client's features.

All 4 metric types are supported: gauge, counter, summary and histogram.

## Contributing

Feel free to submit issues for new features, bugs, documentation.

PRs are also welcome.

## Alternatives

The official prometheus python client: https://github.com/prometheus/client_python
