from dataclasses import dataclass, field
from typing import Literal


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


@dataclass
class Block:
    name: str
    stmts: list[Instruction] = field(default_factory=list)

    def __str__(self) -> str:
        stmts = "\n".join(f"\t{stmt}" for stmt in self.stmts)

        return f"@{self.name}\n{stmts}"


@dataclass
class Function:
    name: str
    rtype: Type | None = None
    blocks: list[Block] = field(default_factory=list)
    export: bool = False

    def __str__(self) -> str:
        export = "export " if self.export else ""
        rtype = f" {self.rtype}" if self.rtype else ""

        header = f"{export}function{rtype} ${self.name}"

        blocks = "\n".join(str(block) for block in self.blocks)

        return f"{header}() {{\n{blocks}\n}}"


@dataclass
class Register:
    name: str
    type: Type | None = None

    def __str__(self) -> str:
        return f"%{self.name}"


@dataclass
class CallArg:
    type: Type
    name: str

    def __str__(self) -> str:
        return f"{self.type} ${self.name}"


@dataclass
class Call(Instruction):
    register: Register | None
    value: Expression
    args: list[CallArg] = field(default_factory=list)

    def __str__(self) -> str:
        if self.register:
            ty = self.register.type or self.value.type

            register = f"{self.register} ={ty} "

        else:
            register = ""

        args = ", ".join(str(arg) for arg in self.args)

        return f"{register}call {self.value}({args})"


@dataclass
class Global(Expression):
    name: str

    def __str__(self) -> str:
        return f"${self.name}"


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
class Data:
    name: str
    items: list[Expression]

    def __str__(self) -> str:
        items = ", ".join(f"{expr.type} {expr}" for expr in self.items)

        return f"data ${self.name} = {{ {items} }}"


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


class Context:
    functions: list[Function]
    data: list[Data]

    def __init__(self) -> None:
        self.functions = []
        self.data = []

    def __str__(self) -> str:
        data = "\n".join(str(x) for x in self.data)
        funcs = "\n".join(str(x) for x in self.functions)

        return f"{data}\n{funcs}"

    def add_func(self, func: Function) -> None:
        self.functions.append(func)

    def add_data(self, data: Data) -> None:
        self.data.append(data)
