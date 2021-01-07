from time import time

from progress import Infinite
from progress.bar import IncrementalBar


class RefreshMixin(Infinite):
    """Only update the progress graphic after a delay.

    This improves performance when the iterations per second is high.
    """

    def __init__(self, *args, **kwargs):
        super(RefreshMixin, self).__init__(*args, **kwargs)
        self._updated_at = None

    def update(self, *args, **kwargs):
        if self._updated_at is not None and time() - self._updated_at < 1:
            return

        self._updated_at = time()
        super(RefreshMixin, self).update(*args, **kwargs)


class IncrementalDelayBar(RefreshMixin, IncrementalBar):
    pass
