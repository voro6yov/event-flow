from message_flow.dependencies import Call, Dependent


def test_dependent__building(simple_func):
    dependent = Dependent.for_call(call=simple_func)
    assert dependent._call == simple_func


def test_call__building(simple_func):
    call = Call(simple_func)
    assert call.name == simple_func.__name__
