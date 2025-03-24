from datetime import datetime
from typing import Annotated
from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, mapped_column


Str = Annotated[str, 255]
LargeStr = Annotated[str, 500]
BigInt = Annotated[int, BigInteger]


class Base(DeclarativeBase):
    type_annotation_map = {
        BigInt: BigInteger(),
        Str: String(255),
        LargeStr: String(500),
    }


IntPK = Annotated[int, mapped_column(BigInteger, primary_key=True)]
TextStr = Annotated[str, mapped_column(Text)]
DateTime = Annotated[datetime, mapped_column(insert_default=datetime.now)]


# Note: To allow distribution of classes across multiple files and avoid circular imports due to relationship definitions, we use the TYPE_CHECKING constant to avoid importing classes directly at runtime. This is a common pattern.
# Check:
# - https://github.com/sqlalchemy/sqlalchemy/discussions/9576#discussioncomment-11867298
# - https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING
# - https://peps.python.org/pep-0484/#runtime-or-type-checking
# - https://peps.python.org/pep-0484/#forward-references

# Default SQLAlchemy type_map: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#mapped-column-derives-the-datatype-and-nullability-from-the-mapped-annotation
