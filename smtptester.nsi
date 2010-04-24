/*******************************************************************************
 * SMTP Tester NSIS script
 * Copyright (c) 2009 Michael Conigliaro <mike [at] conigliaro [dot] org>
 ******************************************************************************/
!include LogicLib.nsh
!include FileFunc.nsh

!define ProductVersionMajor "1"
!define ProductVersionMinor "1"
!define /date ProductBuild "%Y%m%d.%H%M%S"
!define CompanyName "Michael Conigliaro"
!define ProductName "SMTP Tester ${ProductVersionMajor}.${ProductVersionMinor}"
!define ProductNameShort "SMTP Tester"
!define CompanyUrl "http://conigliaro.org"

; Uninstaller
!define Uninstaller "uninstall.exe"

; Registry keys
!define ProductRegKeyRoot "Software\${ProductNameShort}"
!define UninstallRegKeyRoot "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ProductNameShort}"
!define UserStartMenuRegKeyRoot "Software\Microsoft\Windows\CurrentVersion\Explorer\MenuOrder\Start Menu\Programs\${ProductNameShort}"
!define ProductSettingsRegKeyRoot "Software\smtptester"

; Installer version info
LoadLanguageFile "${NSISDIR}\Contrib\Language files\English.nlf"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${ProductName}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${CompanyName}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "© ${CompanyName}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "${ProductName}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${ProductVersionMajor}.${ProductVersionMinor}.${ProductBuild}"
VIProductVersion "${ProductVersionMajor}.${ProductVersionMinor}.${ProductBuild}"

; Installer atributes
Name "${ProductName}"
OutFile "inst/smtptester.exe"
InstallDir "$PROGRAMFILES\${ProductNameShort}"
InstallDirRegKey HKLM "${ProductRegKeyRoot}" "InstallDir"
SetCompressor /FINAL /SOLID lzma


/*******************************************************************************
 * Pages
 ******************************************************************************/
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles


/*******************************************************************************
 * Installer
 ******************************************************************************/
Section
    ; Uninstall old version
    ClearErrors
    ReadRegStr $0 HKLM "${UninstallRegKeyRoot}" "UninstallString"
    ${IfNot} ${Errors}
        ExecWait '$0 /S'
    ${EndIf}

    ; Set install directory
    SetOutPath $INSTDIR

    ; Write the files
    File /r "dist\*"

    ; Use "All Users" shell folders
    SetShellVarContext all

    ; Reset order of start menu entries
    DeleteRegKey HKCU "${UserStartMenuRegKeyRoot}"

    ; Remove program shortcuts
    RMDir /r /REBOOTOK "$SMPROGRAMS\${ProductNameShort}"

    ; Create program shortcuts
    ; FIXME: need icon
    CreateDirectory "$SMPROGRAMS\${ProductNameShort}"
    CreateShortCut "$SMPROGRAMS\${ProductNameShort}\${ProductNameShort}.lnk" "$INSTDIR\smtptester.exe"

    ; Write the installation path into the registry
    WriteRegStr HKLM "${ProductRegKeyRoot}" "InstallDir" "$INSTDIR"

    ; Write the uninstall keys for Windows
    WriteRegStr HKLM "${UninstallRegKeyRoot}" "DisplayName" "${ProductName}"
    WriteRegStr HKLM "${UninstallRegKeyRoot}" "UninstallString" '"$INSTDIR\${Uninstaller}"'
    WriteRegStr HKLM "${UninstallRegKeyRoot}" "InstallLocation" '"$INSTDIR"'
    WriteRegStr HKLM "${UninstallRegKeyRoot}" "Publisher" "${CompanyName}"
    WriteRegStr HKLM "${UninstallRegKeyRoot}" "URLInfoAbout" "${CompanyUrl}"
    WriteRegStr HKLM "${UninstallRegKeyRoot}" "DisplayVersion" "${ProductVersionMajor}.${ProductVersionMinor}"
    WriteRegDWORD HKLM "${UninstallRegKeyRoot}" "VersionMajor" ${ProductVersionMajor}
    WriteRegDWORD HKLM "${UninstallRegKeyRoot}" "VersionMinor" ${ProductVersionMinor}
    WriteRegDWORD HKLM "${UninstallRegKeyRoot}" "NoModify" 1
    WriteRegDWORD HKLM "${UninstallRegKeyRoot}" "NoRepair" 1
    WriteUninstaller "${Uninstaller}"
SectionEnd


/*******************************************************************************
 * Uninstaller
 ******************************************************************************/
Section "Uninstall"

    ; Use "All Users" shell folders
    SetShellVarContext all

    ; Remove files and folders
    Delete "$INSTDIR\*.*"
    RMDir "$INSTDIR"

    ; Reset order of start menu entries
    DeleteRegKey HKCU "${UserStartMenuRegKeyRoot}"

    ; Remove program shortcuts
    RMDir /r "$SMPROGRAMS\${ProductNameShort}"

    ; Remove registry keys
    DeleteRegKey HKLM "${UninstallRegKeyRoot}"
    DeleteRegKey HKLM "${ProductRegKeyRoot}"
    DeleteRegKey HKCU "${UserStartMenuRegKeyRoot}"
    DeleteRegKey HKCU "${ProductSettingsRegKeyRoot}"
SectionEnd
