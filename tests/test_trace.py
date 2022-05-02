from unittest import TestCase

import pandas as pd

from yamm import root
from yamm.constructs.trace import Trace
from yamm.utils.crs import XY_CRS
from tests import get_test_dir



class TestTrace(TestCase):
    def test_trace_from_file(self):
        file = root() / "resources" / "traces" / "sample_trace_1.csv"

        trace = Trace.from_csv(file)

        self.assertEqual(trace.crs, XY_CRS)
        self.assertEqual(len(trace), 1053)

    def test_trace_from_dataframe(self):
        file = root() / "resources" / "traces" / "sample_trace_1.csv"

        df = pd.read_csv(file)

        trace = Trace.from_dataframe(df)

        self.assertEqual(trace.crs, XY_CRS)
        self.assertEqual(len(trace), 1053)


    def test_trace_from_gpx(self):
        file = get_test_dir() / "test_assets" / "test_trace.gpx"
        trace = Trace.from_gpx(file)

        self.assertEqual(trace.crs, XY_CRS)
        self.assertEqual(len(trace), 778)