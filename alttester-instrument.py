#!/usr/bin/env python3
#$python alttester-instrument.py --help
#$python alttester-instrument.py --version=1.8.2 --file="C:\GitHub\EndlessRunnerSampleGame\Assets\Editor\BundleAndBuild.cs" --method="Build()"

import argparse
import urllib.request
from zipfile import ZipFile

# Parse sys args
parser=argparse.ArgumentParser()
parser.add_argument("--version", help="The AltTester Version")
parser.add_argument("--file", help="The build file to modify.")
parser.add_argument("--method", help="The build method to modify.")
args=parser.parse_args()

# Download AltTester version
print(f"version: {args.version}")
url = f"https://github.com/alttester/AltTester-Unity-SDK/releases/download/v.{args.version}/AltTester-v.{args.version}.unitypackage"
urllib.request.urlretrieve(url, "AltTester.unitypackage")
url = f"https://github.com/alttester/AltTester-Unity-SDK/archive/refs/tags/v.{args.version}.zip"
urllib.request.urlretrieve(url, "AltTester.zip")

# ToDo: install unity package

# Modify the build file's using directive
print(f"file: {args.file}")
buildUsingDirectives = \
"""using Altom.AltTesterEditor;
using Altom.AltTester;"""
with open(args.file, 'r+') as f:
    content = f.read()
    f.seek(0, 0)
    f.write(buildUsingDirectives + '\n' + content)

# ToDo: get list of scenes from `/ProjectSettings/EditorBuildSettings.asset` and add to instrumentation list

# Modify the build file's build method
print(f"method: {args.method}")
buildMethodBody = \
"""        var buildTargetGroup = BuildTargetGroup.Android;
        AltBuilder.AddAltTesterInScriptingDefineSymbolsGroup(buildTargetGroup);
        if (buildTargetGroup == UnityEditor.BuildTargetGroup.Standalone) {
            AltBuilder.CreateJsonFileForInputMappingOfAxis();
        }
        var instrumentationSettings = new AltInstrumentationSettings();
        AltBuilder.InsertAltInScene(FirstSceneOfTheGame, instrumentationSettings);"""
with open(args.file, 'r') as infile:
    data = infile.read()
rowData = data.split("\n")
outData = []
line_to_add_code = 0
for i in range(len(rowData)):
    outData.append(rowData[i])
    if args.method in rowData[i]:
        line_to_add_code = i+2
if line_to_add_code > 0:
    outData.insert(line_to_add_code, buildMethodBody)
with open(args.file, 'w') as outfile:
    data = outfile.write('\n'.join(outData))   
