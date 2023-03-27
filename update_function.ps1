$functionName = "amazon-connect-config-portal"

If (!(test-path "$PSScriptRoot\package")) {
    New-Item -ItemType Directory -Force -Path "$PSScriptRoot\package"
}
else {
    Remove-Item "$PSScriptRoot\package\*" -Recurse -Force
}

docker build -t $functionName .
docker create -ti --name dummy $functionName bash
docker cp dummy:/function package
docker rm -f dummy

if (Test-Path -Path "$PSScriptRoot\package.zip") {
    Remove-Item "$PSScriptRoot\package.zip"
}

Write-Host "packaging lambda function $functionName"
if (!(Test-Path "C:\Program Files\7-Zip\7z.exe")) {
        throw "C:\Program Files\7-Zip\7z.exe was not found."
}

$zipVenv = & "C:\Program Files\7-Zip\7z.exe" a -tzip "$PSScriptRoot\package.zip" "$PSScriptRoot\package\function\*"

# In case of NOT using Version
#$updateFunctionResult = aws lambda update-function-code --function-name $functionName --zip-file fileb://package.zip | ConvertFrom-Json
#write-host "update function $functionName success"

# In case of using Version
#$updateFunctionResult = aws lambda update-function-code --function-name $functionName --zip-file fileb://package.zip --publish | ConvertFrom-Json
#$version = $updateFunctionResult.Version
#write-host "update function $functionName to Version $version"

# In case of using Alias
#$updateAliasResult = aws lambda update-alias --function-name $functionName --function-version $version --name ACTIVE | ConvertFrom-Json
#$aliasName = $updateAliasResult.Name
#write-host "update function $functionName alias $aliasName to Version $version"
