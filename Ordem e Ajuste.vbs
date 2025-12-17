Set objShell = CreateObject("WScript.Shell")
Set objFso = CreateObject("Scripting.FileSystemObject")
strPath = objFso.GetParentFolderName(WScript.ScriptFullName)
objShell.Run "python """ & strPath & "\launcher.py""", 0, True