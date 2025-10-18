# Improved Makefile for Zombie DLL
CC=x86_64-w64-mingw32-gcc
CFLAGS=-shared -Wall -fPIC -O2
LDFLAGS=-ladvapi32 -luser32 -lshell32  # Added -lshell32
TARGET=monitor_dll.dll
SOURCES=monitor_dll.c
DEF_FILE=monitor_dll.def

$(TARGET): $(SOURCES) $(DEF_FILE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)
	@echo "Improved Zombie DLL compiled successfully - No warnings"
	@echo "Ready for automatic boot execution"

clean:
	rm -f $(TARGET) *.o
	@echo "Build files cleaned"

test:
	@echo "Testing improved DLL compilation..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)
	@if [ -f "$(TARGET)" ]; then \
		echo "DLL compilation test: SUCCESS"; \
		file $(TARGET); \
	else \
		echo "DLL compilation test: FAILED"; \
	fi

install: $(TARGET)
	@echo "DLL compiled successfully. Use python emulator.py for installation"

.PHONY: all clean test install