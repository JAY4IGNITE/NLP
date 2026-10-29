$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$editDirectory = $PSScriptRoot
$editPlan = Get-Content -LiteralPath (Join-Path $editDirectory 'edit_plan.json') -Raw | ConvertFrom-Json
$narrator = New-Object System.Speech.Synthesis.SpeechSynthesizer
$narrator.SelectVoice('Microsoft Zira Desktop')
$narrator.Rate = 1
$narrator.Volume = 100
try {
    for ($chapterIndex = 0; $chapterIndex -lt $editPlan.Count; $chapterIndex++) {
        for ($sentenceIndex = 0; $sentenceIndex -lt $editPlan[$chapterIndex].sentences.Count; $sentenceIndex++) {
            $voiceFile = Join-Path $editDirectory ('voice_{0:00}_{1:00}.wav' -f $chapterIndex, $sentenceIndex)
            $narrator.SetOutputToWaveFile($voiceFile)
            $narrator.Speak($editPlan[$chapterIndex].sentences[$sentenceIndex])
            $narrator.SetOutputToNull()
        }
        Write-Output ('Narrated: ' + $editPlan[$chapterIndex].title)
    }
} finally {
    $narrator.Dispose()
}
