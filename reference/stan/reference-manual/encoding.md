# Character Encoding - Stan Reference Manual

## Content Characters

Stan programs must use ASCII encoding. All identifiers, operators, and punctuation must be ASCII-compatible. However, UTF-8 and Latin-1 encodings share the first 128 code points with ASCII, making them functionally compatible with Stan programs without risk of data corruption.

## Comment Characters

Content following line comments (`//` or `#`) or block comments (`/* */`) can use any character encoding, since these sections are ignored by the parser.

## String Literals

String literals follow C++ escaping standards. UTF-8 encoded strings are supported, though invalid byte sequences aren't validated. The parser preserves raw bytes between double quotes, allowing Unicode characters to display properly on compatible terminals.

**Key recommendation:** "ASCII is the recommended encoding for maximum portability, because it encodes the ASCII characters (Unicode code points 0-127) using the same sequence of bytes as the UTF-8 encoding" of Unicode and Latin extensions.
