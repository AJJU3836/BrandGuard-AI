param (
    [string]$DocxPath,
    [string]$PdfPath
)

try {
    Write-Host "Opening Word application..."
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    Write-Host "Opening document: $DocxPath"
    $doc = $word.Documents.Open($DocxPath)
    Write-Host "Saving as PDF: $PdfPath"
    # 17 = wdFormatPDF
    $doc.SaveAs([ref]$PdfPath, [ref]17)
    $doc.Close()
    $word.Quit()
    Write-Host "Successfully converted to PDF!"
} catch {
    Write-Error "Conversion error: $_"
    if ($word) { $word.Quit() }
}
