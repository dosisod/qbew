from qbew.nodes import (
    Block,
    Branch,
    ByteType,
    Call,
    CallArg,
    Context,
    Data,
    DoubleType,
    Float,
    Function,
    HalfWordType,
    Halt,
    Int,
    Jump,
    LongType,
    Register,
    Return,
    SingleType,
    String,
    WordType,
)


def test_stringify_basic_types() -> None:
    tests = {
        WordType(): "w",
        LongType(): "l",
        SingleType(): "s",
        DoubleType(): "d",
        ByteType(): "b",
        HalfWordType(): "h",
    }

    for typ, expected in tests.items():
        assert str(typ) == expected


def test_stringify_basic_exprs() -> None:
    tests = {
        Int(123): "123",
        Int(123, type=WordType()): "123",
        Int(123, type=LongType()): "123",
        Float(3.14): "d_3.14",
        Float(3.14, type=DoubleType()): "d_3.14",
        Float(3.14, type=SingleType()): "s_3.14",
        String("hello world"): '"hello world"',
        String("'"): '"\'"',
        String('"'): '"\\x22"',
        String("\x00"): '"\\x00"',
    }

    for typ, expected in tests.items():
        assert str(typ) == expected


def test_stringify_halt() -> None:
    assert str(Halt()) == "hlt"


def test_stringify_return() -> None:
    assert str(Return(Int(123))) == "ret 123"


def test_stringify_void_return() -> None:
    assert str(Return()) == "ret"


def test_stringify_function() -> None:
    block = Block(
        name="start",
        stmts=[Return(Int(123))],
    )

    func = Function(
        name="f",
        rtype=WordType(),
        blocks=[block],
        export=True,
    )

    expected = """\
export function w $f() {
@start
	ret 123
}\
"""

    assert str(func) == expected


def test_stringify_void() -> None:
    func = Function(
        name="f",
        blocks=[Block(name="start", stmts=[Return()])],
        export=True,
    )

    expected = """\
export function $f() {
@start
	ret
}\
"""

    assert str(func) == expected


def test_stringify_call() -> None:
    # This is a call to puts() that uses the global string "str" as an input.
    # This should be made more explicit and expressive in the future.

    call = Call(
        register=Register("r", type=WordType()),
        value="puts",
        args=[CallArg(LongType(), "str")],
    )

    expected = "%r =w call $puts(l $str)"

    assert str(call) == expected


def test_stringify_data() -> None:
    data = Data(
        name="str",
        items=[String("hello world")],
    )

    assert str(data) == 'data $str = { b "hello world" }'


def test_stringify_call_without_register() -> None:
    call = Call(register=None, value="puts", args=[CallArg(LongType(), "str")])

    assert str(call) == "call $puts(l $str)"


def test_stringify_jump() -> None:
    jump = Jump(Block("x"))

    assert str(jump) == "jmp @x"


def test_stringify_branch() -> None:
    branch = Branch(Int(1), Block("t"), Block("f"))

    assert str(branch) == "jnz 1, @t, @f"


def test_hello_world() -> None:
    ctx = Context()

    block = Block(
        name="start",
        stmts=[
            Call(
                register=Register("r", type=WordType()),
                value="puts",
                args=[CallArg(LongType(), "str")],
            ),
        ],
    )

    main = Function(
        name="main",
        rtype=WordType(),
        blocks=[block],
        export=True,
    )

    data = Data(
        name="str",
        items=[String("hello world")],
    )

    ctx.add_func(main)
    ctx.add_data(data)

    expected = """\
data $str = { b "hello world" }
export function w $main() {
@start
	%r =w call $puts(l $str)
}\
"""

    assert str(ctx) == expected
