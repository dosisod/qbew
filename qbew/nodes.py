from dataclasses import dataclass, field


class Type:
    def __str__(self) -> str:
        raise NotImplementedError()


class BaseType(Type): pass
class ExtendedType(BaseType): pass


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
        raise NotImplementedError()


class Expression:
    type: Type

    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass
class Int(Expression):
    value: int
    type: Type = field(default_factory=WordType)

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Float(Expression):
    value: float
    type: Type = field(default_factory=DoubleType)

    def __str__(self) -> str:
        return f"{self.type}_{self.value}"


@dataclass
class String(Expression):
    value: str
    type: Type = field(default_factory=ByteType)

    def __str__(self) -> str:
        escaped = (
            ascii(self.value)[1:-1]
                .replace('"', "\\x22")
                .replace("\\'", "'")
        )

        return f'"{escaped}"'


class Halt(Instruction):
    def __str__(self) -> str:
        return "hlt"


@dataclass
class Return(Instruction):
    expr: Expression

    def __str__(self) -> str:
        return f"ret {self.expr}"


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
    rtype: Type
    blocks: list[Block] = field(default_factory=list)
    export: bool = False

    def __str__(self) -> str:
        export = "export " if self.export else ""
        header = f"{export}function {self.rtype} ${self.name}"

        blocks = "\n".join(str(block) for block in self.blocks)

        return f"{header}() {{\n{blocks}\n}}"


@dataclass
class Register:
    name: str
    type: Type

    def __str__(self) -> str:
        return f"%{self.name} ={self.type}"


@dataclass
class CallArg:
    type: Type
    name: str

    def __str__(self) -> str:
        return f"{self.type} ${self.name}"


@dataclass
class Call(Instruction):
    register: Register | None
    value: str
    args: list[CallArg] = field(default_factory=list)

    def __str__(self) -> str:
        reg = f"{self.register} " if self.register else ""
        args = ", ".join(str(arg) for arg in self.args)

        return f"{reg}call ${self.value}({args})"


@dataclass
class Data:
    name: str
    items: list[Expression]

    def __str__(self) -> str:
        items = ", ".join(f"{expr.type} {expr}" for expr in self.items)

        return f"data ${self.name} = {{ {items} }}"


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
