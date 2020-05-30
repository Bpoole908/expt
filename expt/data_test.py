import os
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd
import pytest

import expt.data
from expt.data import Experiment, Hypothesis, Run, RunList

try:
    from rich.console import Console
    console = Console(markup=False)
    print = console.log
except ImportError:
    pass


def V(x):
    """Print the object and return it."""
    kwargs = dict(_stack_offset=2) if print.__name__ == 'log' else {}
    print(x, **kwargs)
    return x

class _TestBase:
    def setup_method(self, method):
        sys.stdout.write("\n")


class TestRunList(_TestBase):

    def _fixture(self) -> RunList:
       return RunList(
            Run("r%d" % i, pd.DataFrame({"x": [i]}))
            for i in range(16)
       )

    def testRunList(self):
        # instantiation
        r0 = Run("r0", pd.DataFrame({"y" : [1, 2, 3]}))
        r1 = Run("r1", pd.DataFrame({"y" : [1, 4, 9]}))
        runs = RunList([r0, r1])
        print("runs =", runs)

        # unpacking, indexing
        r0_, r1_ = runs
        assert r0_ is r0 and r1_ is r1
        assert runs[0] is r0
        assert runs[-1] is r1

        # iteration
        assert list(runs) == [r0, r1]
        for i, r in enumerate(runs):
            print("r from iterable :", r)
            assert r == [r0, r1][i]

        assert RunList.of(runs) is runs  # no copy should be made

        # list-like operations: extend
        r2 = Run("r1", pd.DataFrame({"y" : [2, 2, 2]}))
        runs.extend([r2])
        assert len(runs) == 3

    def testRunListFilter(self):
        runs = self._fixture()

        # basic operations
        filtered = V(runs.filter(lambda run: run.name in ["r1", "r7"]))
        assert len(filtered) == 2
        assert list(filtered) == [runs[1], runs[7]]

        # invalid argument (fn)
        with pytest.raises(TypeError):
            runs.filter([lambda run: True])

        # filter by string (special case)
        filtered = V(runs.filter("r1*"))  # 1, 10-15
        assert len(filtered) == 7

    def testToHypothesis(self):
        runs = self._fixture()
        h = V(runs.to_hypothesis(name="runlist"))
        assert isinstance(h, Hypothesis)
        assert h.name == "runlist"
        assert not (h.runs is runs)   # should make a new instance

        for i in range(16):
            assert h.runs[i] is runs[i]


class TestHypothesis(_TestBase):

    def testHypothesisCreation(self):
        # instance creation (with auto type conversion)
        h = Hypothesis("hy0", [])
        print(h)
        assert h.name == 'hy0'
        assert isinstance(h.runs, RunList)

        # factory
        r0 = Run("r0", pd.DataFrame({"y": [1, 2, 3]}))
        h = Hypothesis.of([r0])
        print(h)
        assert h.runs.as_list() == [r0]

        h = Hypothesis.of(r0)
        print(h)
        assert h.name == 'r0'
        assert h.runs.as_list() == [r0]

        def generator():
            for i in ["a", "b", "c"]:
                yield Run(i, df=pd.DataFrame())
        h = Hypothesis.of(generator(), name="generator")
        print(h)
        assert h.name == 'generator'
        assert len(h) == 3

    def testHypothesisData(self):
        # test gropued, columns, mean, std, min, max, etc.
        pass


class TestExperiment(_TestBase):

    def testExperimentIndexing(self):
        h0 = Hypothesis("hyp0", Run('r0', pd.DataFrame({"a": [1, 2, 3]})))
        h1 = Hypothesis("hyp1", Run('r1', pd.DataFrame({"a": [4, 5, 6]})))

        ex = Experiment(title="ex", hypotheses=[h0, h1])

        # get hypothesis by name or index
        assert V(ex[0]) == h0
        assert V(ex[1]) == h1
        with pytest.raises(IndexError): V(ex[2])
        assert V(ex["hyp0"]) == h0
        with pytest.raises(KeyError): V(ex["hyp0-not"])

        # nested index
        r = V(ex["hyp0", 'a'])
        assert isinstance(r, pd.DataFrame)
        # assert r is ex["hyp0"]['a']             # TODO
        assert list(r['r0']) == [1, 2, 3]

        # fancy index
        # ----------------
        # (1) by integer index
        r = V(ex[[0, 1]])
        assert r[0] is h0 and r[1] is h1
        # (2) by name?
        r = V(ex[['hyp1', 'hyp0']])
        assert r[0] is h1 and r[1] is h0
        # (3) boolean index (select)
        r = V(ex[[False, True]])
        assert len(r) == 1 and r[0] is h1
        with pytest.raises(IndexError):
            ex[[False, True, False]]
        # (4) non-standard iterable
        r = V(ex[pd.Series([1, 0])])
        assert r[0] is h1 and r[1] is h0

        with pytest.raises(NotImplementedError):  # TODO
            r = V(ex[['hyp1', 'hyp0'], 'a'])


if __name__ == '__main__':
    sys.exit(pytest.main(["-s", "-v"] + sys.argv))
