if (Test-Path -Path "$PSScriptRoot\venv") {
    Remove-Item "$PSScriptRoot\venv" -Recurse -Confirm:$false -Force
}

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install boto3
pip install aws-lambda-powertools
pip install aws-xray-sdk
pip install awslambdaric
pip install PyMySQL
pip install yapf
pip install requests
pip install PyJWT
pip install cryptography


pip freeze > .\requirements.txt