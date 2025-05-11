# Replace "wizzpert" with "wizzpert" in all file contents
Get-ChildItem -Recurse -File | ForEach-Object {
    (Get-Content $_.FullName) -replace 'wizzpert', 'wizzpert' | Set-Content $_.FullName
}

# Rename directories containing "wizzpert"
Get-ChildItem -Recurse -Directory | Where-Object { $_.Name -like "*wizzpert*" } | ForEach-Object {
    Rename-Item -Path $_.FullName -NewName ($_.Name -replace 'wizzpert', 'wizzpert')
}

# Rename files containing "wizzpert"
Get-ChildItem -Recurse -File | Where-Object { $_.Name -like "*wizzpert*" } | ForEach-Object {
    Rename-Item -Path $_.FullName -NewName ($_.Name -replace 'wizzpert', 'wizzpert')
}

Write-Host "Rebranding complete! Replaced all references of 'wizzpert' with 'wizzpert'."
