//Maya ASCII 2016ff07 scene
//Name: animation_v001.ma
//Last modified: Mon, Jan 16, 2017 02:44:23 PM
//Codeset: 1252
file -rdi 1 -ns "Bruce01_" -rfn "Bruce01_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v004/rigDefault.ma";
file -rdi 1 -ns "Bruce02_" -rfn "Bruce02_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v004/rigDefault.ma";
file -r -ns "Bruce01_" -dr 1 -rfn "Bruce01_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v004/rigDefault.ma";
file -r -ns "Bruce02_" -dr 1 -rfn "Bruce02_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v004/rigDefault.ma";
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "A64759E7-4E44-082E-A357-349746868BDB";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -11.605006312070028 4.2605655854061171 4.4191955119574482 ;
	setAttr ".r" -type "double3" -18.93835272960553 -65.800000000001162 -7.7589069627467721e-015 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "5234E64C-4663-3172-5B6F-A29B12526997";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999986;
	setAttr ".coi" 13.072544941224249;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 0 -6.1629758220391547e-033 1.1102230246251565e-016 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "F12302CE-4876-5127-279E-DEA3E3848E7B";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "06F13B79-4EE0-B207-BD31-EC914682EE30";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "922DE3EF-4D35-9EF8-8FA1-78A1C1CFE4C9";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "4882D3EE-40B4-0C8A-221C-8DADBCE77162";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "95F937ED-40FA-A370-0E73-D0A00E404A65";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "4769BCCB-4C30-78E8-01B0-0CA41FAE5774";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "Bruce01_:rigDefault";
	rename -uid "38FBF0F0-43C2-5A0B-2123-2D877FB1F4A7";
	setAttr ".rp" -type "double3" 0 0 1.1102230246251565e-016 ;
	setAttr ".sp" -type "double3" 0 0 1.1102230246251565e-016 ;
createNode transform -n "Bruce02_:rigDefault";
	rename -uid "736041AA-4E0E-FCA3-EFAB-E1AC0D281C0F";
	setAttr ".rp" -type "double3" 0 0 1.1102230246251565e-016 ;
	setAttr ".sp" -type "double3" 0 0 1.1102230246251565e-016 ;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "CC73AA84-4FB0-E330-A590-7DAFF6C43DE8";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "2A8922DB-46C9-96D4-DABB-1A9E7E3883AA";
createNode displayLayer -n "defaultLayer";
	rename -uid "B68707E8-4358-F470-B126-C88C68401C0B";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "E8AAAD18-4CEB-69BD-EF0D-32BCF2DED758";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "76243CFE-44D3-1252-158D-5D8864D62AB9";
	setAttr ".g" yes;
createNode reference -n "Bruce01_RN";
	rename -uid "D6BC6331-47AC-38A0-05C4-67A0B7B4849A";
	setAttr -s 3 ".fn";
	setAttr ".fn[0]" -type "string" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v004/rigDefault.ma";
	setAttr ".fn[1]" -type "string" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v003/rigDefault.ma";
	setAttr ".fn[2]" -type "string" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v002/rigDefault.ma";
	setAttr -s 38 ".phl";
	setAttr ".phl[18]" -type "TdataCompound" ;
	setAttr ".phl[37]" 0;
	setAttr ".phl[38]" 0;
	setAttr ".phl[39]" 0;
	setAttr ".phl[40]" 0;
	setAttr ".phl[41]" 0;
	setAttr ".phl[42]" 0;
	setAttr ".phl[43]" 0;
	setAttr ".phl[44]" 0;
	setAttr ".phl[45]" 0;
	setAttr ".phl[46]" 0;
	setAttr ".phl[47]" 0;
	setAttr ".phl[48]" 0;
	setAttr ".phl[49]" 0;
	setAttr ".phl[50]" 0;
	setAttr ".phl[51]" 0;
	setAttr ".phl[52]" 0;
	setAttr ".phl[53]" 0;
	setAttr ".phl[54]" 0;
	setAttr ".phl[55]" 0;
	setAttr ".phl[56]" 0;
	setAttr ".phl[57]" 0;
	setAttr ".phl[58]" 0;
	setAttr ".phl[59]" 0;
	setAttr ".phl[60]" 0;
	setAttr ".phl[61]" 0;
	setAttr ".phl[62]" 0;
	setAttr ".phl[63]" 0;
	setAttr ".phl[64]" 0;
	setAttr ".phl[65]" 0;
	setAttr ".phl[66]" 0;
	setAttr ".phl[67]" 0;
	setAttr ".phl[68]" 0;
	setAttr ".phl[69]" 0;
	setAttr ".phl[70]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"Bruce01_RN"
		"Bruce01_RN" 4
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:output_GRP|Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.instObjGroups" 
		"Bruce01_RN.placeHolderList[16]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:output_GRP|Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.instObjGroups" 
		"Bruce01_RN.placeHolderList[17]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:output_GRP|Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1|Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1.instObjGroups" 
		"Bruce01_RN.placeHolderList[18]" ""
		5 3 "Bruce01_RN" "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.message" 
		"Bruce01_RN.placeHolderList[36]" ""
		"Bruce01_RN" 42
		2 "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1" 
		"translate" " -type \"double3\" -0.89117113486759247 0.089743094461850303 -0.5599545102689597"
		
		2 "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1" 
		"translateX" " -av"
		2 "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1" 
		"translateY" " -av"
		2 "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1" 
		"translateZ" " -av"
		2 "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1" 
		"rotate" " -type \"double3\" -18.164020058126699 -3.5110228145324416 15.706113122672692"
		
		2 "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1" 
		"rotateX" " -av"
		2 "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1" 
		"rotateY" " -av"
		2 "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1" 
		"rotateZ" " -av"
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[37]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[38]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[39]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP|Bruce01_:Bruce01_:modelDefault.instObjGroups" 
		"Bruce01_RN.placeHolderList[40]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:model_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[41]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:model_GRP|Bruce01_:Bruce01_:pCube1.instObjGroups" 
		"Bruce01_RN.placeHolderList[42]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:model_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.instObjGroups" 
		"Bruce01_RN.placeHolderList[43]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:skeleton_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[44]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:skeleton_GRP|Bruce01_:joint1.instObjGroups" 
		"Bruce01_RN.placeHolderList[45]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:skeleton_GRP|Bruce01_:joint1|Bruce01_:joint1_parentConstraint1.instObjGroups" 
		"Bruce01_RN.placeHolderList[46]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[47]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1.instObjGroups" 
		"Bruce01_RN.placeHolderList[48]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.instObjGroups" 
		"Bruce01_RN.placeHolderList[49]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:pCubeShape1Orig.instObjGroups" 
		"Bruce01_RN.placeHolderList[50]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:output_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[51]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:output_GRP|Bruce01_:Bruce01_:pCube1.instObjGroups" 
		"Bruce01_RN.placeHolderList[52]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[53]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[54]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1.translateX" 
		"Bruce01_RN.placeHolderList[55]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1.translateY" 
		"Bruce01_RN.placeHolderList[56]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1.translateZ" 
		"Bruce01_RN.placeHolderList[57]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1.rotateX" 
		"Bruce01_RN.placeHolderList[58]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1.rotateY" 
		"Bruce01_RN.placeHolderList[59]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1.rotateZ" 
		"Bruce01_RN.placeHolderList[60]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1.instObjGroups" 
		"Bruce01_RN.placeHolderList[61]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:interface_GRP|Bruce01_:controls_GRP|Bruce01_:nurbsCircle1|Bruce01_:nurbsCircleShape1.instObjGroups" 
		"Bruce01_RN.placeHolderList[62]" ""
		5 3 "Bruce01_RN" "Bruce01_:controls_SET.message" "Bruce01_RN.placeHolderList[63]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:out_SET.message" "Bruce01_RN.placeHolderList[64]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:skinCluster1.message" "Bruce01_RN.placeHolderList[65]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:skinCluster1Set.message" "Bruce01_RN.placeHolderList[66]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:bindPose1.message" "Bruce01_RN.placeHolderList[67]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:skinCluster1GroupId.message" "Bruce01_RN.placeHolderList[68]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:skinCluster1GroupParts.message" "Bruce01_RN.placeHolderList[69]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:makeNurbCircle1.message" "Bruce01_RN.placeHolderList[70]" 
		"";
lockNode -l 1 ;
createNode objectSet -n "Bruce01_:rigDefault_CON";
	rename -uid "5B11BE16-45E8-98DC-D130-99844170135B";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "loader" -ln "loader" -dt "string";
	addAttr -ci true -sn "families" -ln "families" -dt "string";
	addAttr -ci true -sn "time" -ln "time" -dt "string";
	addAttr -ci true -sn "version" -ln "version" -dt "string";
	addAttr -ci true -sn "path" -ln "path" -dt "string";
	addAttr -ci true -sn "source" -ln "source" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 22 ".dsm";
	setAttr -s 10 ".dnsm";
	setAttr ".id" -type "string" "pyblish.mindbender.container";
	setAttr ".author" -type "string" "marcus";
	setAttr ".loader" -type "string" "mindbender.maya.pipeline";
	setAttr ".families" -type "string" "mindbender.rig";
	setAttr ".time" -type "string" "20170116T130345Z";
	setAttr ".version" -type "string" "3";
	setAttr ".path" -type "string" "{root}\\assets\\Bruce\\publish\\rigDefault\\v003";
	setAttr ".source" -type "string" "{root}\\assets\\Bruce\\work\\rigging\\marcus\\maya\\scenes\\rig_v001.ma";
createNode objectSet -n "Bruce01_SET";
	rename -uid "4D557A7D-44D1-0194-6E64-24AB0E5B574F";
	addAttr -ci true -sn "subset" -ln "subset" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "family" -ln "family" -dt "string";
	addAttr -ci true -sn "startFrame" -ln "startFrame" -dt "string";
	addAttr -ci true -sn "endFrame" -ln "endFrame" -dt "string";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".subset" -type "string" "Bruce01";
	setAttr ".name" -type "string" "Bruce01";
	setAttr ".family" -type "string" "mindbender.animation";
	setAttr ".startFrame" -type "string" "1.0";
	setAttr ".endFrame" -type "string" "48.0";
	setAttr ".id" -type "string" "pyblish.mindbender.instance";
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "1C322A14-423D-9552-39BE-71B001D9BDF8";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode animCurveTL -n "nurbsCircle1_translateX";
	rename -uid "95C8F393-4031-799B-9B8A-369B4F2AB41D";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 -1.7080780084962193;
createNode animCurveTL -n "nurbsCircle1_translateY";
	rename -uid "1ABD361F-4798-2438-AC4E-DD9B0EC4F21F";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 0.17200759771854646;
createNode animCurveTL -n "nurbsCircle1_translateZ";
	rename -uid "C77658B6-4EA2-039E-09F2-3B9C4A372160";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 -1.0732461446821731;
createNode animCurveTA -n "nurbsCircle1_rotateX";
	rename -uid "E881B40F-4570-28A2-9D66-DBAC84049C18";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 -34.814371778076179;
createNode animCurveTA -n "nurbsCircle1_rotateY";
	rename -uid "BFDAABB7-4C1D-3034-F606-30859927D485";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 -6.7294603945205145;
createNode animCurveTA -n "nurbsCircle1_rotateZ";
	rename -uid "F6A814E2-447F-01D8-B465-AB8812126200";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 30.103383485122666;
createNode reference -n "Bruce02_RN";
	rename -uid "8A37ECB3-4260-0AF7-72C1-1C989E8FBB45";
	setAttr -s 2 ".fn";
	setAttr ".fn[0]" -type "string" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v003/rigDefault.ma{1}";
	setAttr ".fn[1]" -type "string" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v002/rigDefault.ma{1}";
	setAttr -s 38 ".phl";
	setAttr ".phl[16]" -type "TdataCompound" ;
	setAttr ".phl[17]" -type "TdataCompound" ;
	setAttr ".phl[18]" -type "TdataCompound" ;
	setAttr ".phl[37]" 0;
	setAttr ".phl[38]" 0;
	setAttr ".phl[39]" 0;
	setAttr ".phl[40]" 0;
	setAttr ".phl[41]" 0;
	setAttr ".phl[42]" 0;
	setAttr ".phl[43]" 0;
	setAttr ".phl[44]" 0;
	setAttr ".phl[45]" 0;
	setAttr ".phl[46]" 0;
	setAttr ".phl[47]" 0;
	setAttr ".phl[48]" 0;
	setAttr ".phl[49]" 0;
	setAttr ".phl[50]" 0;
	setAttr ".phl[51]" 0;
	setAttr ".phl[52]" 0;
	setAttr ".phl[53]" 0;
	setAttr ".phl[54]" 0;
	setAttr ".phl[55]" 0;
	setAttr ".phl[56]" 0;
	setAttr ".phl[57]" 0;
	setAttr ".phl[58]" 0;
	setAttr ".phl[59]" 0;
	setAttr ".phl[60]" 0;
	setAttr ".phl[61]" 0;
	setAttr ".phl[62]" 0;
	setAttr ".phl[63]" 0;
	setAttr ".phl[64]" 0;
	setAttr ".phl[65]" 0;
	setAttr ".phl[66]" 0;
	setAttr ".phl[67]" 0;
	setAttr ".phl[68]" 0;
	setAttr ".phl[69]" 0;
	setAttr ".phl[70]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"Bruce02_RN"
		"Bruce02_RN" 4
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:output_GRP|Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.instObjGroups" 
		"Bruce02_RN.placeHolderList[16]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:output_GRP|Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.instObjGroups" 
		"Bruce02_RN.placeHolderList[17]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:output_GRP|Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1|Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1.instObjGroups" 
		"Bruce02_RN.placeHolderList[18]" ""
		5 3 "Bruce02_RN" "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.message" 
		"Bruce02_RN.placeHolderList[36]" ""
		"Bruce02_RN" 43
		2 "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:output_GRP" 
		"visibility" " 0"
		2 "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1" 
		"translate" " -type \"double3\" -0.17589120339766551 1.6500784526506651 -2.4814430990120475"
		
		2 "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1" 
		"translateX" " -av"
		2 "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1" 
		"translateY" " -av"
		2 "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1" 
		"translateZ" " -av"
		2 "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1" 
		"rotate" " -type \"double3\" 94.411086488812913 58.032714430548772 92.244102708530988"
		
		2 "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1" 
		"rotateX" " -av"
		2 "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1" 
		"rotateY" " -av"
		2 "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1" 
		"rotateZ" " -av"
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP.instObjGroups" 
		"Bruce02_RN.placeHolderList[37]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP.instObjGroups" 
		"Bruce02_RN.placeHolderList[38]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP.instObjGroups" 
		"Bruce02_RN.placeHolderList[39]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP|Bruce02_:Bruce01_:modelDefault.instObjGroups" 
		"Bruce02_RN.placeHolderList[40]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP|Bruce02_:Bruce01_:modelDefault|Bruce02_:Bruce01_:model_GRP.instObjGroups" 
		"Bruce02_RN.placeHolderList[41]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP|Bruce02_:Bruce01_:modelDefault|Bruce02_:Bruce01_:model_GRP|Bruce02_:Bruce01_:pCube1.instObjGroups" 
		"Bruce02_RN.placeHolderList[42]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP|Bruce02_:Bruce01_:modelDefault|Bruce02_:Bruce01_:model_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.instObjGroups" 
		"Bruce02_RN.placeHolderList[43]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:skeleton_GRP.instObjGroups" 
		"Bruce02_RN.placeHolderList[44]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:skeleton_GRP|Bruce02_:joint1.instObjGroups" 
		"Bruce02_RN.placeHolderList[45]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:skeleton_GRP|Bruce02_:joint1|Bruce02_:joint1_parentConstraint1.instObjGroups" 
		"Bruce02_RN.placeHolderList[46]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP.instObjGroups" 
		"Bruce02_RN.placeHolderList[47]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1.instObjGroups" 
		"Bruce02_RN.placeHolderList[48]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.instObjGroups" 
		"Bruce02_RN.placeHolderList[49]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:pCubeShape1Orig.instObjGroups" 
		"Bruce02_RN.placeHolderList[50]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:output_GRP.instObjGroups" 
		"Bruce02_RN.placeHolderList[51]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:output_GRP|Bruce02_:Bruce01_:pCube1.instObjGroups" 
		"Bruce02_RN.placeHolderList[52]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP.instObjGroups" 
		"Bruce02_RN.placeHolderList[53]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP.instObjGroups" 
		"Bruce02_RN.placeHolderList[54]" ""
		5 4 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1.translateX" 
		"Bruce02_RN.placeHolderList[55]" ""
		5 4 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1.translateY" 
		"Bruce02_RN.placeHolderList[56]" ""
		5 4 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1.translateZ" 
		"Bruce02_RN.placeHolderList[57]" ""
		5 4 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1.rotateX" 
		"Bruce02_RN.placeHolderList[58]" ""
		5 4 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1.rotateY" 
		"Bruce02_RN.placeHolderList[59]" ""
		5 4 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1.rotateZ" 
		"Bruce02_RN.placeHolderList[60]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1.instObjGroups" 
		"Bruce02_RN.placeHolderList[61]" ""
		5 3 "Bruce02_RN" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:interface_GRP|Bruce02_:controls_GRP|Bruce02_:nurbsCircle1|Bruce02_:nurbsCircleShape1.instObjGroups" 
		"Bruce02_RN.placeHolderList[62]" ""
		5 3 "Bruce02_RN" "Bruce02_:controls_SET.message" "Bruce02_RN.placeHolderList[63]" 
		""
		5 3 "Bruce02_RN" "Bruce02_:out_SET.message" "Bruce02_RN.placeHolderList[64]" 
		""
		5 3 "Bruce02_RN" "Bruce02_:skinCluster1.message" "Bruce02_RN.placeHolderList[65]" 
		""
		5 3 "Bruce02_RN" "Bruce02_:skinCluster1Set.message" "Bruce02_RN.placeHolderList[66]" 
		""
		5 3 "Bruce02_RN" "Bruce02_:bindPose1.message" "Bruce02_RN.placeHolderList[67]" 
		""
		5 3 "Bruce02_RN" "Bruce02_:skinCluster1GroupId.message" "Bruce02_RN.placeHolderList[68]" 
		""
		5 3 "Bruce02_RN" "Bruce02_:skinCluster1GroupParts.message" "Bruce02_RN.placeHolderList[69]" 
		""
		5 3 "Bruce02_RN" "Bruce02_:makeNurbCircle1.message" "Bruce02_RN.placeHolderList[70]" 
		"";
lockNode -l 1 ;
createNode objectSet -n "Bruce02_:rigDefault_CON";
	rename -uid "7A313469-4283-330B-C190-4681D13DBBF3";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "loader" -ln "loader" -dt "string";
	addAttr -ci true -sn "families" -ln "families" -dt "string";
	addAttr -ci true -sn "time" -ln "time" -dt "string";
	addAttr -ci true -sn "version" -ln "version" -dt "string";
	addAttr -ci true -sn "path" -ln "path" -dt "string";
	addAttr -ci true -sn "source" -ln "source" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 22 ".dsm";
	setAttr -s 10 ".dnsm";
	setAttr ".id" -type "string" "pyblish.mindbender.container";
	setAttr ".author" -type "string" "marcus";
	setAttr ".loader" -type "string" "mindbender.maya.pipeline";
	setAttr ".families" -type "string" "mindbender.rig";
	setAttr ".time" -type "string" "20170116T130345Z";
	setAttr ".version" -type "string" "3";
	setAttr ".path" -type "string" "{root}\\assets\\Bruce\\publish\\rigDefault\\v003";
	setAttr ".source" -type "string" "{root}\\assets\\Bruce\\work\\rigging\\marcus\\maya\\scenes\\rig_v001.ma";
createNode objectSet -n "Bruce02_SET";
	rename -uid "4D4D3AED-4C7C-072C-5285-C2B6DF334765";
	addAttr -ci true -sn "subset" -ln "subset" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "family" -ln "family" -dt "string";
	addAttr -ci true -sn "startFrame" -ln "startFrame" -dt "string";
	addAttr -ci true -sn "endFrame" -ln "endFrame" -dt "string";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".subset" -type "string" "Bruce02";
	setAttr ".name" -type "string" "Bruce02";
	setAttr ".family" -type "string" "mindbender.animation";
	setAttr ".startFrame" -type "string" "1.0";
	setAttr ".endFrame" -type "string" "48.0";
	setAttr ".id" -type "string" "pyblish.mindbender.instance";
createNode animCurveTL -n "nurbsCircle1_translateX1";
	rename -uid "9A23A874-4D1A-06CA-34FF-E099A90C3221";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0.70840795608917873 21 -0.76542397638889526;
createNode animCurveTL -n "nurbsCircle1_translateY1";
	rename -uid "6F8B3F03-4508-6005-EF99-20AEF9F60B69";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 1.6142071819408139 21 1.6739926331238992;
createNode animCurveTL -n "nurbsCircle1_translateZ1";
	rename -uid "1013BE98-4BFA-9F6A-30B7-C3962CA4FFD8";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0.18878114025646076 21 -4.2615925918577204;
createNode animCurveTA -n "nurbsCircle1_rotateX1";
	rename -uid "F4118F55-45F7-3FC4-B412-37AF56EA9222";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 25.885582126770192 21 140.09475606350807;
createNode animCurveTA -n "nurbsCircle1_rotateY1";
	rename -uid "0FFF4FAB-4471-2359-3074-5E8C0E969DF5";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 56.155058763752109 21 59.284484875079876;
createNode animCurveTA -n "nurbsCircle1_rotateZ1";
	rename -uid "3DF31DB1-4D34-ED70-51D5-38BB03AF0589";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 -7.0891414851672883 21 158.46626550432987;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "71E69630-4BFB-5E2D-EF41-46ACD84C36C7";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -351.19046223542108 -215.47618191393627 ;
	setAttr ".tgi[0].vh" -type "double2" 785.71425449280639 196.4285636232016 ;
createNode reference -n "sharedReferenceNode";
	rename -uid "1D3433B0-458D-CD33-3FC0-C6827BEE0893";
	setAttr ".ed" -type "dataReferenceEdits" 
		"sharedReferenceNode";
select -ne :time1;
	setAttr ".o" 13;
	setAttr ".unw" 13;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr -s 6 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "Bruce01_RN.phl[37]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[38]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[39]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[40]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[41]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[42]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[43]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[44]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[45]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[46]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[47]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[48]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[49]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[50]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[51]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[52]" "Bruce01_SET.dsm" -na;
connectAttr "Bruce01_RN.phl[53]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[54]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "nurbsCircle1_translateX.o" "Bruce01_RN.phl[55]";
connectAttr "nurbsCircle1_translateY.o" "Bruce01_RN.phl[56]";
connectAttr "nurbsCircle1_translateZ.o" "Bruce01_RN.phl[57]";
connectAttr "nurbsCircle1_rotateX.o" "Bruce01_RN.phl[58]";
connectAttr "nurbsCircle1_rotateY.o" "Bruce01_RN.phl[59]";
connectAttr "nurbsCircle1_rotateZ.o" "Bruce01_RN.phl[60]";
connectAttr "Bruce01_RN.phl[61]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[62]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[63]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[64]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[65]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[66]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[67]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[68]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[69]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[70]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[37]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[38]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[39]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[40]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[41]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[42]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[43]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[44]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[45]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[46]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[47]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[48]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[49]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[50]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[51]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[52]" "Bruce02_SET.dsm" -na;
connectAttr "Bruce02_RN.phl[53]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[54]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "nurbsCircle1_translateX1.o" "Bruce02_RN.phl[55]";
connectAttr "nurbsCircle1_translateY1.o" "Bruce02_RN.phl[56]";
connectAttr "nurbsCircle1_translateZ1.o" "Bruce02_RN.phl[57]";
connectAttr "nurbsCircle1_rotateX1.o" "Bruce02_RN.phl[58]";
connectAttr "nurbsCircle1_rotateY1.o" "Bruce02_RN.phl[59]";
connectAttr "nurbsCircle1_rotateZ1.o" "Bruce02_RN.phl[60]";
connectAttr "Bruce02_RN.phl[61]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[62]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[63]" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[64]" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[65]" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[66]" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[67]" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[68]" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[69]" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[70]" "Bruce02_:rigDefault_CON.dnsm" -na;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "Bruce01_:rigDefault.msg" "Bruce01_RN.asn[0]";
connectAttr "sharedReferenceNode.sr" "Bruce01_RN.sr";
connectAttr "Bruce01_RN.phl[16]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[18]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:rigDefault.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[36]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[17]" "Bruce01_SET.dsm" -na;
connectAttr "Bruce02_:rigDefault.msg" "Bruce02_RN.asn[0]";
connectAttr "sharedReferenceNode.sr" "Bruce02_RN.sr";
connectAttr "Bruce02_RN.phl[16]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[18]" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:rigDefault.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[36]" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.msg" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[17]" "Bruce02_SET.dsm" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of animation_v001.ma
