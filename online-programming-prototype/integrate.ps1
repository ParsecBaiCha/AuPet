$targetFrontend = 'D:\GITHUB\aupet-new\2026081247-萌宠智伴-前端代码\frontend'
$targetBackend = 'D:\GITHUB\aupet-new\backend'
$stagingSource = 'D:\GITHUB\aupet\integration'
Copy-Item -LiteralPath "$targetFrontend\src\views\student\AILearning.vue" -Destination "$stagingSource\AILearning.original.vue"
Copy-Item -LiteralPath "$targetBackend\app.py" -Destination "$stagingSource\app.original.py"
Copy-Item -LiteralPath "$stagingSource\AILearning.vue" -Destination "$targetFrontend\src\views\student\AILearning.vue"
Copy-Item -LiteralPath "$stagingSource\OnlineProgrammingLesson.vue" -Destination "$targetFrontend\src\views\student\OnlineProgrammingLesson.vue"
New-Item -ItemType Directory -Path "$targetFrontend\public\online-programming" -Force | Out-Null
Get-ChildItem -LiteralPath "$stagingSource\public\online-programming" -File | Copy-Item -Destination "$targetFrontend\public\online-programming"
Copy-Item -LiteralPath "$stagingSource\app.py" -Destination "$targetBackend\app.py"
