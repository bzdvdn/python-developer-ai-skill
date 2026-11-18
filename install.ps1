#Requires -Version 5.1
<#
.SYNOPSIS
Install the Python Developer Agent Skill Suite on Windows.

.DESCRIPTION
Copies the python-* skill directories into a host's skills location. Run from a
clone, or pipe the script straight from GitHub:

  irm https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.ps1 | iex

Default: project install into .\.agents\skills.

.PARAMETER HostName
agents, opencode, claude, codex, kilo, trae, or all. Default: agents.

.PARAMETER Global
Install into the user-level directory instead of the current project.

.PARAMETER Destination
Explicit destination directory. Overrides -HostName and -Global.

.PARAMETER Ref
Override the download ref: a branch, tag, or commit. A release asset defaults to
its own tag; the source script defaults to the latest release. Use HEAD for the
repository default branch, or a tag such as v0.1.4.

.PARAMETER Repo
Source repository. Default: bzdvdn/python-developer-ai-skill.

.EXAMPLE
.\install.ps1 -HostName claude -Global

.EXAMPLE
.\install.ps1 -HostName opencode -Destination C:\tools\skills
#>
[CmdletBinding()]
param(
    [ValidateSet('agents', 'opencode', 'claude', 'codex', 'kilo', 'trae', 'all')]
    [string]$HostName = 'agents',

    [switch]$Global,

    [string]$Destination = '',

    [string]$Ref = '',

    [string]$Repo = 'bzdvdn/python-developer-ai-skill'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$AllHosts = @('agents', 'opencode', 'claude', 'codex', 'kilo', 'trae')

function Get-SkillDestination {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][bool]$GlobalScope
    )

    if ($GlobalScope) {
        switch ($Name) {
            'agents' { return (Join-Path $HOME '.agents\skills') }
            'opencode' { return (Join-Path $HOME '.config\opencode\skills') }
            'claude' { return (Join-Path $HOME '.claude\skills') }
            'codex' { return (Join-Path $HOME '.codex\skills') }
            'kilo' { return (Join-Path $HOME '.kilo\skills') }
            'trae' { return (Join-Path $HOME '.trae\skills') }
        }
    }
    else {
        $root = (Get-Location).Path
        switch ($Name) {
            'agents' { return (Join-Path $root '.agents\skills') }
            'opencode' { return (Join-Path $root '.opencode\skills') }
            'claude' { return (Join-Path $root '.claude\skills') }
            'codex' { return (Join-Path $root '.codex\skills') }
            'kilo' { return (Join-Path $root '.kilo\skills') }
            'trae' { return (Join-Path $root '.trae\skills') }
        }
    }

    throw "Unknown host: $Name"
}

function Get-LocalSource {
    if ([string]::IsNullOrEmpty($PSScriptRoot)) {
        return $null
    }
    if (Test-Path (Join-Path $PSScriptRoot 'python-coder\SKILL.md')) {
        return $PSScriptRoot
    }
    return $null
}

function Resolve-LatestReleaseTag {
    $headers = @{
        'User-Agent' = 'python-developer-ai-skill-installer'
        'Accept' = 'application/vnd.github+json'
    }
    if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) {
        $headers['Authorization'] = "Bearer $($env:GITHUB_TOKEN)"
    }

    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -Headers $headers
    $tag = $release.tag_name
    if ([string]::IsNullOrWhiteSpace($tag)) {
        throw 'Could not determine the latest release tag. Pass -Ref <tag|branch|commit>.'
    }
    return $tag
}

function Save-RemoteSource {
    param(
        [Parameter(Mandatory = $true)][string]$TempRoot,
        [Parameter(Mandatory = $true)][string]$Ref
    )

    $zipPath = Join-Path $TempRoot 'suite.zip'
    $extractRoot = Join-Path $TempRoot 'src'
    $url = "https://github.com/$Repo/archive/$Ref.zip"

    Write-Host "Downloading $Repo@$Ref ..."
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $extractRoot -Force

    $root = Get-ChildItem -Path $extractRoot -Directory | Select-Object -First 1
    if ($null -eq $root) {
        throw 'Downloaded archive is empty.'
    }
    if (-not (Test-Path (Join-Path $root.FullName 'python-coder\SKILL.md'))) {
        throw 'Downloaded archive does not look like this suite.'
    }
    return $root.FullName
}

function Install-Skills {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Target
    )

    $skills = @(
        Get-ChildItem -Path $Source -Directory -Filter 'python-*' |
            Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }
    )
    if ($skills.Count -eq 0) {
        throw "No skills found in $Source"
    }

    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    foreach ($skill in $skills) {
        $skillTarget = Join-Path $Target $skill.Name
        if (Test-Path $skillTarget) {
            Remove-Item -Recurse -Force $skillTarget
        }
        Copy-Item -Recurse -Force $skill.FullName $skillTarget
    }

    Write-Host "Installed $($skills.Count) skills into $Target"
}

if ([string]::IsNullOrWhiteSpace($Repo)) {
    throw '-Repo must not be empty.'
}
if (-not [string]::IsNullOrWhiteSpace($Destination) -and $HostName -eq 'all') {
    throw '-Destination cannot be combined with -HostName all.'
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("python-agent-skill-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot | Out-Null

try {
    $source = Get-LocalSource
    if ($null -eq $source) {
        $refToUse = $Ref
        if ([string]::IsNullOrWhiteSpace($refToUse)) {
            $refToUse = Resolve-LatestReleaseTag
            Write-Host "Latest release: $refToUse"
        }
        $source = Save-RemoteSource -TempRoot $tempRoot -Ref $refToUse
    }

    $targets = @()
    if (-not [string]::IsNullOrWhiteSpace($Destination)) {
        $targets = @($Destination)
    }
    elseif ($HostName -eq 'all') {
        $targets = @($AllHosts | ForEach-Object { Get-SkillDestination -Name $_ -GlobalScope $Global.IsPresent })
    }
    else {
        $targets = @(Get-SkillDestination -Name $HostName -GlobalScope $Global.IsPresent)
    }

    foreach ($target in $targets) {
        Install-Skills -Source $source -Target $target
    }

    Write-Host 'Restart the host or start a new session so it rescans skills.'
}
finally {
    if (Test-Path $tempRoot) {
        Remove-Item -Recurse -Force $tempRoot -ErrorAction SilentlyContinue
    }
}
