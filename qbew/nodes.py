from dataclasses import dataclass, field


class Type:
    def __str__(self) -> str:
        raise NotImplementedError()


class BaseType(Type): pass


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


class ExtendedType(BaseType):
    def __str__(self) -> str:
        raise NotImplementedError()


class ByteType(ExtendedType):
    def __str__(self) -> str:
        return "b"


class HalfWordType(ExtendedType):
    def __str__(self) -> str:
        return "h"


class Statement:
    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass
class Expression:
    type: Type

    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass
class IntExpression:
    value: int
    type: Type

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class ReturnStatement(Statement):
    expr: Expression

    def __str__(self) -> str:
        return f"ret {self.expr}"


@dataclass
class Block:
    name: str
    stmts: list[Statement] = field(default_factory=list)

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


class Context:
    functions: list[Function]

    def __init__(self) -> None:
        self.functions = []

    def __str__(self) -> str:
        return "\n".join(str(x) for x in self.functions)

    def add_func(self, func: Function) -> None:
        self.functions.append(func)
