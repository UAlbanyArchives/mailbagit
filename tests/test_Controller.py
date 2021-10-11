import pytest

from mailbag.controller import Controller
import mailbag


def test_read():

    with pytest.raises(Exception) as exc:
        c = Controller({})
        c.read("msg", ["data/sample1.msg", ""])
    assert exc.type == ValueError
    assert "Mailbag currently only reads one input source." in str(exc.value)
