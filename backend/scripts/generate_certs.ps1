if (!(Test-Path "nginx/certs")) {
    New-Item -ItemType Directory -Path "nginx/certs" | Out-Null
}

$cert = New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\CurrentUser\My" -NotAfter (Get-Date).AddYears(1)

$certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
$certPem = "-----BEGIN CERTIFICATE-----`n" + [Convert]::ToBase64String($certBytes, [Base64FormattingOptions]::InsertLineBreaks) + "`n-----END CERTIFICATE-----"
[System.IO.File]::WriteAllText("nginx/certs/server.crt", $certPem)

$rsa = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($cert)
$keyBytes = $rsa.ExportPkcs8PrivateKey()
$keyPem = "-----BEGIN PRIVATE KEY-----`n" + [Convert]::ToBase64String($keyBytes, [Base64FormattingOptions]::InsertLineBreaks) + "`n-----END PRIVATE KEY-----"
[System.IO.File]::WriteAllText("nginx/certs/server.key", $keyPem)

Write-Host "SSL certificates successfully generated in nginx/certs/"
