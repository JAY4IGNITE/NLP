$ErrorActionPreference = 'Stop'
$editPlan = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'edit_plan.json') -Raw | ConvertFrom-Json
$narrator = New-Object -ComObject SAPI.SpVoice
$voiceToken = New-Object -ComObject SAPI.SpObjectToken
$voiceToken.SetId('HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\MSTTS_V110_enIN_RaviM')
$narrator.Voice = $voiceToken
$narrator.Rate = 0
$narrator.Volume = 100
for ($chapterIndex = 0; $chapterIndex -lt $editPlan.Count; $chapterIndex++) {
    for ($sentenceIndex = 0; $sentenceIndex -lt $editPlan[$chapterIndex].sentences.Count; $sentenceIndex++) {
        $voiceFile = Join-Path $PSScriptRoot ('voice_{0:00}_{1:00}.wav' -f $chapterIndex, $sentenceIndex)
        $voiceStream = New-Object -ComObject SAPI.SpFileStream
        try {
            $voiceStream.Open($voiceFile, 3, $false)
            $narrator.AudioOutputStream = $voiceStream
            $narrator.Speak($editPlan[$chapterIndex].sentences[$sentenceIndex]) | Out-Null
        } finally {
            $voiceStream.Close()
        }
    }
    Write-Output ('Narrated: ' + $editPlan[$chapterIndex].title)
}
Write-Output ('Voice: ' + $narrator.Voice.GetDescription())
