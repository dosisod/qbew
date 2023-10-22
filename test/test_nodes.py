from qbew.nodes import (
    Aggregate,
    AggregateType,
    Alloc,
    Arg,
    Block,
    Branch,
    ByteType,
    Call,
    CallArg,
    Comparison,
    ComparisonOper,
    Context,
    Data,
    DoubleType,
    ExportLinkage,
    Float,
    Function,
    Global,
    HalfWordType,
    Halt,
    Int,
    Jump,
    Load,
    LongType,
    OpaqueType,
    Register,
    Return,
    SectionLinkage,
    SingleType,
    Store,
    String,
    ThreadLinkage,
    Type,
    WordType,
    Zeros,
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
        linkage=ExportLinkage(),
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
        linkage=ExportLinkage(),
    )

    expected = """\
export function $f() {
@start
	ret
}\
"""

    assert str(func) == expected


def test_stringify_call() -> None:
    call = Call(
        register=Register("r", type=WordType()),
        value=Global("puts"),
        args=[CallArg(LongType(), Global("str"))],
    )

    expected = "%r =w call $puts(l $str)"

    assert str(call) == expected


def test_stringify_variadic_call() -> None:
    call = Call(
        register=None,
        value=Global("printf"),
        args=[
            CallArg(LongType(), Global("str")),
            ...,
            CallArg(WordType(), Register("x")),
        ],
    )

    expected = "call $printf(l $str, ..., w %x)"

    assert str(call) == expected


def test_stringify_data() -> None:
    data = Data(
        name="str",
        items=[String("hello world")],
    )

    assert str(data) == 'data $str = { b "hello world" }'


def test_stringify_data_with_linkage() -> None:
    thread = Data(
        name="x",
        items=[Int(123)],
        linkage=ThreadLinkage(),
    )

    assert str(thread) == "thread data $x = { w 123 }"

    section = Data(
        name="x",
        items=[Int(123)],
        linkage=SectionLinkage(section=".bbs", flags="some_flag"),
    )

    assert str(section) == 'section ".bbs" "some_flag" data $x = { w 123 }'


def test_stringify_with_alignment() -> None:
    data = Data(
        name="str",
        items=[String("hello world")],
        align=8,
    )

    assert str(data) == 'data $str = align 8 { b "hello world" }'


def test_stringify_call_without_register() -> None:
    call = Call(
        register=None,
        value=Global("puts"),
        args=[CallArg(LongType(), Global("str"))],
    )

    assert str(call) == "call $puts(l $str)"


def test_stringify_jump() -> None:
    jump = Jump(Block("x"))

    assert str(jump) == "jmp @x"


def test_stringify_branch() -> None:
    branch = Branch(Int(1), Block("t"), Block("f"))

    assert str(branch) == "jnz 1, @t, @f"


def test_stringify_global() -> None:
    assert str(Global("f")) == "$f"


def test_stringify_thread_global() -> None:
    assert str(Global("f", thread=True)) == "thread $f"


def test_stringify_register() -> None:
    assert str(Register("r")) == "%r"


def test_stringify_alloc() -> None:
    alloc = Alloc(Register("r"), 4, 8)

    assert str(alloc) == "%r =l alloc4 8"


def test_stringify_store() -> None:
    store = Store(Int(123), Register("r"))

    assert str(store) == "storew 123, %r"


def test_stringify_load() -> None:
    l1 = Load(Register("l1", WordType()), WordType(), Global("x"))

    assert str(l1) == "%l1 =w loaduw $x"

    l2 = Load(Register("l2", WordType()), ByteType(), Global("x"))

    assert str(l2) == "%l2 =w loadub $x"

    l3 = Load(Register("l3", WordType()), ByteType(), Global("x"), signed=True)

    assert str(l3) == "%l3 =w loadsb $x"

    l4 = Load(Register("l4", DoubleType()), DoubleType(), Global("x"))

    assert str(l4) == "%l4 =d loadd $x"


def test_hello_world() -> None:
    ctx = Context()

    block = Block(
        name="start",
        stmts=[
            Call(
                register=Register("r", type=WordType()),
                value=Global("puts"),
                args=[CallArg(LongType(), Global("str"))],
            ),
        ],
    )

    main = Function(
        name="main",
        rtype=WordType(),
        blocks=[block],
        linkage=ExportLinkage(),
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


def test_stringify_zero_initializer() -> None:
    data = Data("x", [Zeros(8)])

    assert str(data) == "data $x = { z 8 }"


def test_hash_types() -> None:
    # Same types should be equal
    assert hash(WordType()) == hash(WordType())
    assert hash(DoubleType()) == hash(DoubleType())

    # Different types should be different
    assert hash(WordType()) != hash(DoubleType())

    # Subclasses should not be equal
    assert hash(Type()) != hash(WordType())


def test_type_equality() -> None:
    # Same types should be equal
    assert WordType() == WordType()
    assert DoubleType() == DoubleType()

    # Different types should be different
    assert WordType() != DoubleType()

    # Subclasses should not be equal
    assert Type() != WordType()


def test_stringify_empty_blocks() -> None:
    func = Function(
        "f",
        rtype=None,
        blocks=[
            Block("b1"),
            Block("b2", [Return()]),
        ],
    )

    expected = """\
function $f() {
@b1
@b2
	ret
}\
"""

    assert str(func) == expected


def test_stringify_func_arg() -> None:
    arg = Arg(WordType(), "x")

    assert str(arg) == "w %x"


def test_stringify_variadic_func_arg() -> None:
    func = Function(
        "add",
        rtype=WordType(),
        args=[Arg(WordType(), "x"), ...],
    )

    expected = """\
function w $add(w %x, ...) {

}\
"""

    assert str(func) == expected


def test_stringify_aggregate() -> None:
    nums = Aggregate(name="nums", items=[WordType(), LongType()], align=4)

    assert str(nums) == "type :nums = align 4 { w, l }"


def test_stringify_aggregate_no_alignment() -> None:
    nums = Aggregate(name="nums", items=[WordType(), LongType()])

    assert str(nums) == "type :nums = { w, l }"


def test_stringify_opaque_type() -> None:
    nums = OpaqueType(name="ptr", size=8, align=16)

    assert str(nums) == "type :ptr = align 16 { 8 }"


def test_stringify_align_type() -> None:
    assert str(AggregateType("x")) == ":x"


def test_stringify_aggregate_in_context() -> None:
    ctx = Context()

    agg = Aggregate("t", [WordType()])
    ctx.add_aggregate(agg)

    assert str(ctx) == "type :t = { w }"


def test_stringify_comparison() -> None:
    cmp = Comparison(
        register=Register("r"),
        op=ComparisonOper.EQUAL,
        lhs=Int(1),
        rhs=Int(2),
    )

    assert str(cmp) == "%r =w ceqw 1, 2"


def test_stringify_comparison_with_explicit_instruction_type() -> None:
    cmp = Comparison(
        register=Register("r"),
        op=ComparisonOper.EQUAL,
        lhs=Global("x"),
        rhs=Global("x"),
        type=LongType(),
    )

    assert str(cmp) == "%r =w ceql $x, $x"


def test_stringify_comparison_with_explicit_register_type() -> None:
    cmp = Comparison(
        register=Register("r", LongType()),
        op=ComparisonOper.EQUAL,
        lhs=Int(1),
        rhs=Int(2),
    )

    assert str(cmp) == "%r =l ceqw 1, 2"


def test_stringify_function_with_debug_info() -> None:
    block = Block(
        name="start",
        stmts=[Return(Int(0), line=1)],
    )

    func = Function(
        name="main",
        rtype=WordType(),
        blocks=[block],
        linkage=ExportLinkage(),
        file="dbg_file.xyz",
    )

    expected = """\
dbgfile "dbg_file.xyz"
export function w $main() {
@start
	dbgloc 1
	ret 0
}\
"""

    assert str(func) == expected
