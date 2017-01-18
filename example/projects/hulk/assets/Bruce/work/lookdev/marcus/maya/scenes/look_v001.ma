//Maya ASCII 2016ff07 scene
//Name: look_v001.ma
//Last modified: Tue, Jan 17, 2017 04:29:56 PM
//Codeset: 1252
file -rdi 1 -ns "Bruce01_" -rfn "Bruce01_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/modelDefault/v001/modelDefault.ma";
file -r -ns "Bruce01_" -dr 1 -rfn "Bruce01_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/modelDefault/v001/modelDefault.ma";
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "BB4DEF4D-42E2-E7CD-A1CE-0283136A14EF";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 3.1270059390555716 1.9420249725223819 2.4255544378558573 ;
	setAttr ".r" -type "double3" -26.138352729602605 52.200000000000074 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "DC05E4AE-435E-114D-240F-E18FA81B808A";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999986;
	setAttr ".coi" 4.4082810105290822;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "CEF160E8-428A-F5CF-CB7E-1EA993C79F7E";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "A3C25BF4-4BC5-5671-C90D-C6A67A988F82";
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
	rename -uid "7EC421F6-46C1-F084-712C-49BB68381319";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "EC9E9089-4070-D0F2-B9CE-FC83DA3C8D75";
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
	rename -uid "1850FB47-4F7E-D1D9-D6B4-428E096EBCC1";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "B3E54CD7-4679-7DF3-B01E-0CA3680BDEB0";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "Bruce01_:modelDefault";
	rename -uid "26F7CEBD-4FE9-6CC7-7C61-3EB6C19945B4";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "DAF30F82-4D36-19D7-5C56-6AABB3FD6B3E";
	setAttr -s 4 ".lnk";
	setAttr -s 4 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "649CE484-4667-7171-272B-4385015E5049";
createNode displayLayer -n "defaultLayer";
	rename -uid "909D821B-4D60-E39E-AB8C-C1BACF733FDC";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "CE19C507-4E92-7706-FFA1-3D93EB2E458A";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "066D91BF-4AF1-01FB-AE50-9483A369EB46";
	setAttr ".g" yes;
createNode reference -n "Bruce01_RN";
	rename -uid "FB34C787-484C-9339-A679-638535125BE2";
	setAttr -s 14 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".phl[5]" 0;
	setAttr ".phl[6]" 0;
	setAttr ".phl[7]" 0;
	setAttr ".phl[8]" 0;
	setAttr ".phl[9]" 0;
	setAttr ".phl[10]" 0;
	setAttr ".phl[11]" 0;
	setAttr ".phl[12]" 0;
	setAttr ".phl[13]" 0;
	setAttr ".phl[14]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"Bruce01_RN"
		"Bruce01_RN" 0
		"Bruce01_RN" 18
		2 "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0" 
		"instObjGroups.objectGroups" " -s 2"
		2 "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0" 
		"instObjGroups.objectGroups[0].objectGrpCompList" " -type \"componentList\" 4 \"f[0:1]\" \"f[3:4]\" \"f[6:18]\" \"f[20:23]\""
		
		2 "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0" 
		"instObjGroups.objectGroups[1].objectGrpCompList" " -type \"componentList\" 3 \"f[2]\" \"f[5]\" \"f[19]\""
		
		3 "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.instObjGroups" 
		":initialShadingGroup.dagSetMembers" "-na"
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT.instObjGroups" 
		"Bruce01_RN.placeHolderList[1]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH.instObjGroups" 
		"Bruce01_RN.placeHolderList[2]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE.instObjGroups" 
		"Bruce01_RN.placeHolderList[3]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0.instObjGroups" 
		"Bruce01_RN.placeHolderList[4]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0.instObjGroups" 
		"Bruce01_RN.placeHolderList[5]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.instObjGroups" 
		"Bruce01_RN.placeHolderList[6]" ":initialShadingGroup.dsm"
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.instObjGroups.objectGroups[0]" 
		"Bruce01_RN.placeHolderList[7]" ""
		5 4 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.instObjGroups.objectGroups[0].objectGroupId" 
		"Bruce01_RN.placeHolderList[8]" ""
		5 4 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.instObjGroups.objectGroups[0].objectGrpColor" 
		"Bruce01_RN.placeHolderList[9]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.instObjGroups.objectGroups[1]" 
		"Bruce01_RN.placeHolderList[10]" ""
		5 4 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.instObjGroups.objectGroups[1].objectGroupId" 
		"Bruce01_RN.placeHolderList[11]" ""
		5 4 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.instObjGroups.objectGroups[1].objectGrpColor" 
		"Bruce01_RN.placeHolderList[12]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.compInstObjGroups.compObjectGroups[0]" 
		"Bruce01_RN.placeHolderList[13]" ""
		5 4 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:BRUCE|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.compInstObjGroups.compObjectGroups[0].compObjectGroupId" 
		"Bruce01_RN.placeHolderList[14]" "";
lockNode -l 1 ;
createNode objectSet -n "Bruce01_:modelDefault_CON";
	rename -uid "6034FC3F-4DB6-4D17-4322-9489B85667FF";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "loader" -ln "loader" -dt "string";
	addAttr -ci true -sn "families" -ln "families" -dt "string";
	addAttr -ci true -sn "time" -ln "time" -dt "string";
	addAttr -ci true -sn "version" -ln "version" -dt "string";
	addAttr -ci true -sn "path" -ln "path" -dt "string";
	addAttr -ci true -sn "source" -ln "source" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 6 ".dsm";
	setAttr ".id" -type "string" "pyblish.mindbender.container";
	setAttr ".author" -type "string" "marcus";
	setAttr ".loader" -type "string" "mindbender.maya.pipeline";
	setAttr ".families" -type "string" "mindbender.model";
	setAttr ".time" -type "string" "20170117T161717Z";
	setAttr ".version" -type "string" "1";
	setAttr ".path" -type "string" "{root}\\assets\\Bruce\\publish\\modelDefault\\v001";
	setAttr ".source" -type "string" "{root}\\assets\\Bruce\\work\\modeling\\marcus\\maya\\scenes\\model_v001.ma";
createNode blinn -n "blinn1";
	rename -uid "EDCC49EE-494E-DAE5-A77F-3DB69C4D4BE6";
	setAttr ".c" -type "float3" 0 1 0 ;
createNode shadingEngine -n "blinn1SG";
	rename -uid "6BCB8CC7-4D85-432A-76C2-E1B9B8AB7C11";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
	setAttr -s 2 ".gn";
createNode materialInfo -n "materialInfo1";
	rename -uid "E06F1692-4292-9D4A-E43F-86BEEE8D31D4";
createNode blinn -n "blinn2";
	rename -uid "FDC4A825-4B9D-CB5A-E870-F8819E5F2EB0";
	setAttr ".c" -type "float3" 1 0 0 ;
createNode shadingEngine -n "blinn2SG";
	rename -uid "99A55F32-4CB6-3A64-966D-2CACDFC70D17";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo2";
	rename -uid "F77F9207-46DC-7C49-F242-28A2CD6CA0EC";
createNode groupId -n "groupId1";
	rename -uid "557B9B99-4DB7-465C-8CEA-46B37ABE0D01";
	setAttr ".ihi" 0;
createNode groupId -n "groupId2";
	rename -uid "90F5DC63-4FE3-539F-8311-EFA82B58FA87";
	setAttr ".ihi" 0;
createNode groupId -n "groupId3";
	rename -uid "0BC4EC05-44EE-C7C7-3D45-62A278814EA5";
	setAttr ".ihi" 0;
createNode objectSet -n "lookdevDefault_SET";
	rename -uid "02144206-4AE0-99DE-7079-94B854E5D48B";
	addAttr -ci true -sn "subset" -ln "subset" -dt "string";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "family" -ln "family" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	setAttr ".ihi" 0;
	setAttr ".subset" -type "string" "lookdevDefault";
	setAttr ".id" -type "string" "pyblish.mindbender.instance";
	setAttr ".family" -type "string" "mindbender.lookdev";
	setAttr ".name" -type "string" "lookdevDefault";
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "42A9DF29-4344-91C4-3E72-FE916C81842D";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "28EE963A-4773-0795-7C6C-749C7FAEAECB";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -449.99998211860731 -189.2857067641761 ;
	setAttr ".tgi[0].vh" -type "double2" 434.52379225738525 234.52380020467101 ;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 4 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 6 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "Bruce01_RN.phl[1]" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[2]" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[3]" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[4]" "lookdevDefault_SET.dsm" -na;
connectAttr "Bruce01_RN.phl[5]" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[6]" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[7]" "blinn1SG.dsm" -na;
connectAttr "groupId1.id" "Bruce01_RN.phl[8]";
connectAttr "blinn1SG.mwc" "Bruce01_RN.phl[9]";
connectAttr "Bruce01_RN.phl[10]" "blinn2SG.dsm" -na;
connectAttr "groupId3.id" "Bruce01_RN.phl[11]";
connectAttr "blinn2SG.mwc" "Bruce01_RN.phl[12]";
connectAttr "Bruce01_RN.phl[13]" "blinn1SG.dsm" -na;
connectAttr "groupId2.id" "Bruce01_RN.phl[14]";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "blinn1SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "blinn2SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "blinn1SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "blinn2SG.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "Bruce01_:modelDefault.msg" "Bruce01_RN.asn[0]";
connectAttr "Bruce01_RN.msg" "Bruce01_:modelDefault_CON.dnsm" -na;
connectAttr "Bruce01_:modelDefault.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "blinn1.oc" "blinn1SG.ss";
connectAttr "groupId1.msg" "blinn1SG.gn" -na;
connectAttr "groupId2.msg" "blinn1SG.gn" -na;
connectAttr "blinn1SG.msg" "materialInfo1.sg";
connectAttr "blinn1.msg" "materialInfo1.m";
connectAttr "blinn2.oc" "blinn2SG.ss";
connectAttr "groupId3.msg" "blinn2SG.gn" -na;
connectAttr "blinn2SG.msg" "materialInfo2.sg";
connectAttr "blinn2.msg" "materialInfo2.m";
connectAttr "blinn1SG.pa" ":renderPartition.st" -na;
connectAttr "blinn2SG.pa" ":renderPartition.st" -na;
connectAttr "blinn1.msg" ":defaultShaderList1.s" -na;
connectAttr "blinn2.msg" ":defaultShaderList1.s" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of look_v001.ma
