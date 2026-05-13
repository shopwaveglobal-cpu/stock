# What bytes produce the garbled Korean text in CP949?
# The popup says: (?좏겙을 찾을 수 없습니다
# Let's find the byte values

chars = "(?좏겙"
print("Characters:", chars)
print("Unicode codepoints:", [ord(c) for c in chars])

try:
    b = chars.encode("cp949")
    print("CP949 hex:", b.hex())
    print("CP949 bytes:", list(b))

    ascii_view = ""
    for x in b:
        if 32 <= x < 127:
            ascii_view += chr(x)
        else:
            ascii_view += "[{:02x}]".format(x)
    print("ASCII view:", ascii_view)
except Exception as e:
    print("Error:", e)

# Now: if these bytes were ORIGINALLY a different encoding, what would they say?
# CP949 bytes -> try interpreting as UTF-8
print("\n--- Reverse: what was the original string? ---")
b2 = chars.encode("cp949")
try:
    as_utf8 = b2.decode("utf-8", errors="replace")
    print("If UTF-8:", repr(as_utf8))
except Exception as e:
    print("UTF-8 decode error:", e)

try:
    as_ascii = b2.decode("ascii", errors="replace")
    print("If ASCII:", repr(as_ascii))
except Exception as e:
    print("ASCII decode error:", e)

try:
    as_latin1 = b2.decode("latin-1")
    print("If Latin-1:", repr(as_latin1))
except Exception as e:
    print("Latin-1 decode error:", e)
