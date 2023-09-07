from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from types import EllipsisType


class Type:
    def __str__(self) -> str:
        raise NotImplementedError

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Type) and type(o) == type(self)

    def __hash__(self) -> int:
        return hash(self.__class__)


class BaseType(Type):
    pass


class ExtendedType(BaseType):
    pass


class WordType(BaseType):
    def __str__(self) -> str:
        return "w"


class LongType(BaseType):
    def __str__(self) -> str:
        return "l"


class SingleType(BaseType):
    def __str__(self) -> str:
        return "s"


class DoubleType(BaseType):
    def __str__(self) -> str:
        return "d"


class ByteType(ExtendedType):
    def __str__(self) -> str:
        return "b"


class HalfWordType(ExtendedType):
    def __str__(self) -> str:
        return "h"


class AggregateType(Type):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f":{self.name}"


class Instruction:
    def __str__(self) -> str:
        raise NotImplementedError


class Expression:
    type: Type

    def __str__(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Int(Expression):
    value: int
    type: Type = field(default_factory=WordType)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Float(Expression):
    value: float
    type: Type = field(default_factory=DoubleType)

    def __str__(self) -> str:
        return f"{self.type}_{self.value}"


@dataclass(frozen=True)
class String(Expression):
    value: str
    type: Type = field(default_factory=ByteType)

    def __str__(self) -> str:
        escaped = (
            ascii(self.value)[1:-1].replace('"', "\\x22").replace("\\'", "'")
        )

        return f'"{escaped}"'


class Halt(Instruction):
    def __str__(self) -> str:
        return "hlt"


@dataclass
class Return(Instruction):
    expr: Expression | None = None

    def __str__(self) -> str:
        return f"ret {self.expr}" if self.expr else "ret"


class ComparisonOper(Enum):
    # Integer and float ops
    EQUAL = "eq"
    NOT_EQUAL = "ne"

    # Integer only ops
    SIGNED_LESS_THAN_EQUAL = "sle"
    SIGNED_LESS_THAN = "slt"
    SIGNED_GREATER_THAN_EQUAL = "sge"
    SIGNED_GREATER_THAN = "sgt"
    UNSIGNED_LESS_THAN_EQUAL = "ule"
    UNSIGNED_LESS_THAN = "ult"
    UNSIGNED_GREATER_THAN_EQUAL = "uge"
    UNSIGNED_GREATER_THAN = "ugt"

    # Float only ops
    LESS_THAN_EQUAL = "le"
    LESS_THAN = "lt"
    GREATER_THAN_EQUAL = "ge"
    GREATER_THAN = "gt"
    ORDERED = "o"
    UNORDERED = "uo"


@dataclass
class Comparison(Instruction):
    register: Register
    op: ComparisonOper
    lhs: Expression
    rhs: Expression
    type: Type | None = None

    def __str__(self) -> str:
        register_type = self.register.type or WordType()

        op_type = self.type or self.lhs.type

        inst = f"c{self.op.value}{op_type} {self.lhs}, {self.rhs}"

        return f"{self.register} ={register_type} {inst}"


@dataclass
class Block:
    name: str
    stmts: list[Instruction] = field(default_factory=list)

    def __str__(self) -> str:
        stmts = "\n".join(f"\t{stmt}" for stmt in self.stmts)
        name = f"@{self.name}"

        return f"{name}\n{stmts}" if stmts else name


class Linkage:
    def __str__(self) -> str:
        raise NotImplementedError


class ExportLinkage(Linkage):
    def __str__(self) -> str:
        return "export"


class ThreadLinkage(Linkage):
    def __str__(self) -> str:
        return "thread"


@dataclass
class SectionLinkage(Linkage):
    section: str
    flags: str | None = None

    def __str__(self) -> str:
        flags = f' "{self.flags}"' if self.flags else ""

        return f'section "{self.section}"{flags}'


@dataclass
class Arg:
    type: Type
    name: str

    def __str__(self) -> str:
        return f"{self.type} %{self.name}"


@dataclass
class Function:
    name: str
    rtype: Type | None = None
    blocks: list[Block] = field(default_factory=list)
    linkage: Linkage | None = None
    args: list[Arg | EllipsisType] = field(default_factory=list)

    def __str__(self) -> str:
        linkage = f"{self.linkage} " if self.linkage else ""
        rtype = f" {self.rtype}" if self.rtype else ""

        args = ", ".join(
            "..." if arg is ... else str(arg) for arg in self.args
        )
        header = f"{linkage}function{rtype} ${self.name}({args})"

        blocks = "\n".join(str(block) for block in self.blocks)

        return f"{header} {{\n{blocks}\n}}"


@dataclass
class Register:
    name: str
    type: Type | None = None

    def __str__(self) -> str:
        return f"%{self.name}"


@dataclass
class CallArg:
    type: Type
    name: Register | Global

    def __str__(self) -> str:
        return f"{self.type} {self.name}"


@dataclass
class Call(Instruction):
    register: Register | None
    value: Expression
    args: list[CallArg | EllipsisType] = field(default_factory=list)

    def __str__(self) -> str:
        if self.register:
            ty = self.register.type or self.value.type

            register = f"{self.register} ={ty} "

        else:
            register = ""

        args = ", ".join(
            "..." if arg is ... else str(arg) for arg in self.args
        )

        return f"{register}call {self.value}({args})"


@dataclass
class Global(Expression):
    name: str
    thread: bool = False

    def __str__(self) -> str:
        thread = "thread " if self.thread else ""

        return f"{thread}${self.name}"


@dataclass
class Jump(Instruction):
    block: Block

    def __str__(self) -> str:
        return f"jmp @{self.block.name}"


@dataclass
class Branch(Instruction):
    condition: Expression
    true: Block
    false: Block

    def __str__(self) -> str:
        return f"jnz {self.condition}, @{self.true.name}, @{self.false.name}"


@dataclass
class Zeros:
    count: int

    def __str__(self) -> str:
        assert self.count > 0

        return f"z {self.count}"


@dataclass
class Data:
    name: str
    items: list[Expression | Zeros]
    linkage: Linkage | None = None

    def __str__(self) -> str:
        items = ", ".join(
            str(expr) if isinstance(expr, Zeros) else f"{expr.type} {expr}"
            for expr in self.items
        )

        linkage = f"{self.linkage} " if self.linkage else ""

        return f"{linkage}data ${self.name} = {{ {items} }}"


@dataclass
class Alloc:
    register: Register
    align: Literal[4, 8, 16]
    bytes: int

    def __str__(self) -> str:
        return f"{self.register} =l alloc{self.align} {self.bytes}"


@dataclass
class Store:
    expr: Expression
    addr: Register | Global

    def __str__(self) -> str:
        return f"store{self.expr.type} {self.expr}, {self.addr}"


@dataclass
class Load:
    register: Register
    load_type: Type
    addr: Register | Global
    signed: bool = False

    def __str__(self) -> str:
        if self.load_type in (WordType(), HalfWordType(), ByteType()):
            suffix = "s" if self.signed else "u"
        else:
            suffix = ""

        ty = f"{suffix}{self.load_type}"

        return f"{self.register} ={self.register.type} load{ty} {self.addr}"


class AggregateBase:
    pass


@dataclass
class Aggregate(AggregateBase):
    name: str
    items: list[Type]
    align: int | None = None

    def __str__(self) -> str:
        items = ", ".join(str(item) for item in self.items)
        align = f" align {self.align}" if self.align else ""

        return f"type :{self.name} ={align} {{ {items} }}"


@dataclass
class OpaqueType(AggregateBase):
    name: str
    size: int
    align: int

    def __str__(self) -> str:
        return f"type :{self.name} = align {self.align} {{ {self.size} }}"


class Context:
    aggregates: list[Aggregate]
    data: list[Data]
    functions: list[Function]

    def __init__(self) -> None:
        self.aggregates = []
        self.data = []
        self.functions = []

    def __str__(self) -> str:
        return "\n".join(
            str(x) for x in self.aggregates + self.data + self.functions
        )

    def add_aggregate(self, aggregate: Aggregate) -> None:
        self.aggregates.append(aggregate)

    def add_data(self, data: Data) -> None:
        self.data.append(data)

    def add_func(self, func: Function) -> None:
        self.functions.append(func)
