
import platform
import sys
import os
import re


def supports_color():
	"""
	Returns True if the running system's terminal supports color, and False
	otherwise.
	"""
	plat = sys.platform
	supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
												  'ANSICON' in os.environ)
	# isatty is not always implemented, #6223.
	is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
	if not supported_platform or not is_a_tty:
		return False
	return True

#------------------------------------------------------------------------------
# ANSI Terminal Colors
#------------------------------------------------------------------------------
class Colors:
	HEADER			= '\033[95m'
	OKBLUE			= '\033[94m'
	OKGREEN			= '\033[92m'
	WARNING			= '\033[93m'
	FAIL			= '\033[91m'
	BOLD			= '\033[1m'
	UNDERLINE		= '\033[4m'

	RED				= "\033[31m"
	GREEN			= "\033[32m"
	YELLOW			= "\033[38;5;226m"

	DEFAULT			= "\033[0m"
	BUFFED_STAT		= "\033[32m"
	DAMAGED_HEALTH	= "\033[31m"
	CARD_NAME		= "\033[38;5;85m"
	CARD_TEXT		= "\033[38;5;249m"
	PLAYABLE		= "\033[38;5;112m\033[48;5;235m"
	ACTIVATED		= "\033[38;5;190m"

	EXCEPTION		= "\033[38;5;226m"

def set_text_color(color):
	sys.stdout.write(color)

#------------------------------------------------------------------------------
# Windows Platform Console Colors
# https://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
#------------------------------------------------------------------------------
if not supports_color():

	from ctypes import windll, Structure, c_short, c_ushort, byref

	SHORT = c_short
	WORD = c_ushort

	class COORD(Structure):
	  """struct in wincon.h."""
	  _fields_ = [
	    ("X", SHORT),
	    ("Y", SHORT)]

	class SMALL_RECT(Structure):
	  """struct in wincon.h."""
	  _fields_ = [
	    ("Left", SHORT),
	    ("Top", SHORT),
	    ("Right", SHORT),
	    ("Bottom", SHORT)]

	class CONSOLE_SCREEN_BUFFER_INFO(Structure):
	  """struct in wincon.h."""
	  _fields_ = [
	    ("dwSize", COORD),
	    ("dwCursorPosition", COORD),
	    ("wAttributes", WORD),
	    ("srWindow", SMALL_RECT),
	    ("dwMaximumWindowSize", COORD)]

	# winbase.h
	STD_INPUT_HANDLE = -10
	STD_OUTPUT_HANDLE = -11
	STD_ERROR_HANDLE = -12

	# wincon.h
	FOREGROUND_BLACK     = 0x0000
	FOREGROUND_BLUE      = 0x0001
	FOREGROUND_GREEN     = 0x0002
	FOREGROUND_CYAN      = 0x0003
	FOREGROUND_RED       = 0x0004
	FOREGROUND_MAGENTA   = 0x0005
	FOREGROUND_YELLOW    = 0x0006
	FOREGROUND_GREY      = 0x0007
	FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

	BACKGROUND_BLACK     = 0x0000
	BACKGROUND_BLUE      = 0x0010
	BACKGROUND_GREEN     = 0x0020
	BACKGROUND_CYAN      = 0x0030
	BACKGROUND_RED       = 0x0040
	BACKGROUND_MAGENTA   = 0x0050
	BACKGROUND_YELLOW    = 0x0060
	BACKGROUND_GREY      = 0x0070
	BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

	Colors.BLACK		= 0x0000
	Colors.NAVY			= 0x0001
	Colors.DARK_GREEN	= 0x0002
	Colors.TEAL			= 0x0003
	Colors.MAROON		= 0x0004
	Colors.PURPLE		= 0x0005
	Colors.OLIVE		= 0x0006
	Colors.GRAY			= 0x0007

	Colors.DARK_GRAY	= 0x0000 | FOREGROUND_INTENSITY
	Colors.BLUE			= 0x0001 | FOREGROUND_INTENSITY
	Colors.GREEN		= 0x0002 | FOREGROUND_INTENSITY
	Colors.CYAN			= 0x0003 | FOREGROUND_INTENSITY
	Colors.RED			= 0x0004 | FOREGROUND_INTENSITY
	Colors.MAGENTA		= 0x0005 | FOREGROUND_INTENSITY
	Colors.YELLOW		= 0x0006 | FOREGROUND_INTENSITY
	Colors.WHITE		= 0x0007 | FOREGROUND_INTENSITY

	Colors.DEFAULT			= Colors.GRAY
	Colors.BUFFED_STAT		= Colors.GREEN
	Colors.DAMAGED_HEALTH	= Colors.RED
	Colors.CARD_NAME		= Colors.TEAL
	Colors.CARD_TEXT		= Colors.DARK_GRAY
	Colors.EXCEPTION		= Colors.YELLOW


	stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
	SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
	GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

	def get_text_attr():
		"""Returns the character attributes (colors) of the console screen
		buffer."""
		csbi = CONSOLE_SCREEN_BUFFER_INFO()
		GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
		return csbi.wAttributes

	def set_text_attr(color):
		"""Sets the character attributes (colors) of the console screen
		buffer. Color is a combination of foreground and background color,
		foreground and background intensity."""
		SetConsoleTextAttribute(stdout_handle, color)

    # Override the set_text_color with the Windows version.
	set_text_color = set_text_attr



def push_color(color):
	set_text_color(color)
def pop_color():
	set_text_color(Colors.DEFAULT)




def color_print(text):
	index = 0
	for match in re.finditer("{(?P<color>[_A-Za-z0-9]*)}", text):
		color_name = match.group("color")
		color = Colors.DEFAULT
		if not color_name == "":
			color = getattr(Colors, color_name.upper())

		sys.stdout.write(text[index:match.start()])
		sys.stdout.flush()
		index = match.end()

		set_text_color(color)

	sys.stdout.write(text[index:])
	sys.stdout.flush()



