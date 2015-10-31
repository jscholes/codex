import _winreg
from ctypes import byref, wintypes, windll

def AssocQueryKeyW():
    ASSOCF_NONE = 0x00000000
    ASSOCF_INIT_NOREMAPCLSID = 0x00000001
    ASSOCF_INIT_BYEXENAME = 0x00000002
    ASSOCF_OPEN_BYEXENAME = 0x00000002
    ASSOCF_INIT_DEFAULTTOSTAR = 0x00000004
    ASSOCF_INIT_DEFAULTTOFOLDER = 0x00000008
    ASSOCF_NOUSERSETTINGS = 0x00000010
    ASSOCF_NOTRUNCATE = 0x00000020
    ASSOCF_VERIFY = 0x00000040
    ASSOCF_REMAPRUNDLL = 0x00000080
    ASSOCF_NOFIXUPS = 0x00000100
    ASSOCF_IGNOREBASECLASS = 0x00000200
    ASSOCF_INIT_IGNOREUNKNOWN = 0x00000400
    ASSOCF_INIT_FIXED_PROGID = 0x00000800
    ASSOCF_IS_PROTOCOL = 0x00001000
    ASSOCF_INIT_FOR_FILE = 0x00002000

    ASSOCKEY_SHELLEXECCLASS = 1
    ASSOCKEY_APP = 2
    ASSOCKEY_CLASS = 3
    ASSOCKEY_BASECLASS = 4

    windll.shlwapi.AssocQueryKeyW.argtypes = [wintypes.ULONG, wintypes.ULONG, wintypes.POINTER(wintypes.LPCSTR), wintypes.POINTER(wintypes.LPCSTR), wintypes.POINTER(wintypes.HKEY)]
    windll.shlwapi.AssocQueryKeyW.restype = wintypes.HRESULT

    flags = ASSOCF_INIT_NOREMAPCLSID|ASSOCF_INIT_DEFAULTTOSTAR|ASSOCF_INIT_DEFAULTTOFOLDER
    key = ASSOCKEY_CLASS
    pszAssoc = wintypes.LPCSTR('.epub')
    pszExtra = wintypes.LPSTR(None)
    phkeyOut = wintypes.HKEY()

    result = windll.shlwapi.AssocQueryKeyW(flags, key, byref(pszAssoc), byref(pszExtra), byref(phkeyOut))
    print result
    print phkeyOut.value
    return phkeyOut

def RegOpenKeyExW(hKey):
    windll.advapi32.RegOpenKeyExW.argtypes = [wintypes.HKEY, wintypes.LPCWSTR, wintypes.DWORD, wintypes.ULONG, wintypes.HANDLE]
    windll.advapi32.RegOpenKeyExW.restype = wintypes.LONG

    KEY_QUERY_VALUE = 0x00000001

    hKey = hKey
    lpSubKey = wintypes.LPCWSTR('shell')
    ulOptions = wintypes.DWORD(0)
    samDesired = wintypes.ULONG(KEY_QUERY_VALUE)
    phkResult = wintypes.HANDLE()

    result = windll.advapi32.RegOpenKeyExW(hKey, lpSubKey, ulOptions, samDesired, phkResult)
    print result
    print phkResult.value
    return phkResult

phkeyOut = AssocQueryKeyW()
phkResult = RegOpenKeyExW(phkeyOut)