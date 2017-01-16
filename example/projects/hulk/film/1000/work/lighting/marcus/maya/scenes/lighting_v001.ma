//Maya ASCII 2016ff07 scene
//Name: lighting_v001.ma
//Last modified: Mon, Jan 16, 2017 02:50:29 PM
//Codeset: 1252
file -rdi 1 -ns "Bruce01_" -rfn "Bruce01_RN" -typ "Alembic" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/film/1000/publish/Bruce01/v002/Bruce01.abc";
file -rdi 1 -ns "Bruce02_" -rfn "Bruce02_RN" -typ "Alembic" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/film/1000/publish/Bruce02/v002/Bruce02.abc";
file -rdi 1 -ns "Bruce_" -rfn "Bruce_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/lookdevDefault/v001/lookdevDefault.ma";
file -r -ns "Bruce01_" -dr 1 -rfn "Bruce01_RN" -typ "Alembic" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/film/1000/publish/Bruce01/v002/Bruce01.abc";
file -r -ns "Bruce02_" -dr 1 -rfn "Bruce02_RN" -typ "Alembic" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/film/1000/publish/Bruce02/v002/Bruce02.abc";
file -r -ns "Bruce_" -dr 1 -rfn "Bruce_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/lookdevDefault/v001/lookdevDefault.ma";
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "A2D5908D-4BBD-8220-EADD-98B3C549859C";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0.011990693110110584 3.6563750720178714 -8.4862819006822434 ;
	setAttr ".r" -type "double3" -18.338352729603649 -181.39999999999893 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "FFE2295A-4810-679C-A99D-B78A8BD55990";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 8.9112236545797785;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "CFBCEAFA-4428-76D0-6122-20945D673162";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "7BAD7590-4440-E5F2-E59F-7BAAA7F13891";
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
	rename -uid "C16092A4-413D-448E-0E13-5D87A3D0EAFD";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "612D4688-4B87-605A-6990-848050D99FBC";
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
	rename -uid "24515098-47A8-BB76-5ACC-B4B381FCA38D";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "76CF87ED-438F-874E-3D25-2AB9166431D2";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "Bruce01_:Bruce01";
	rename -uid "6CB35CF5-40C9-41CC-E5B2-129492919407";
createNode transform -n "Bruce02_:Bruce02";
	rename -uid "70403992-4A4C-AB2D-13C0-48B677660057";
	setAttr ".rp" -type "double3" 0.7084079384803772 1.6142071485519409 0.18878114223480225 ;
	setAttr ".sp" -type "double3" 0.7084079384803772 1.6142071485519409 0.18878114223480225 ;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "AB3CCA80-433C-7AB0-7AD0-6D88C64F9B2E";
	setAttr -s 3 ".lnk";
	setAttr -s 3 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "4F57B82D-4A8D-ECB6-E17F-F5B948E00289";
createNode displayLayer -n "defaultLayer";
	rename -uid "E01C8D59-464F-3099-496D-F6AB38BCC5E7";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "1607F3F1-479D-AEB3-300A-8DB7B07ED2D2";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "C3B0A679-4361-71A9-B1C8-6AA730C2E2E0";
	setAttr ".g" yes;
createNode reference -n "Bruce01_RN";
	rename -uid "40E190E1-465A-D728-2E7B-D6810FEADF13";
	setAttr -s 4 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"Bruce01_RN"
		"Bruce01_RN" 0
		"Bruce01_RN" 5
		3 "|Bruce01_:Bruce01|Bruce01_:pCube1|Bruce01_:pCubeShape1.instObjGroups" 
		":initialShadingGroup.dagSetMembers" "-na"
		5 3 "Bruce01_RN" "|Bruce01_:Bruce01|Bruce01_:pCube1.instObjGroups" "Bruce01_RN.placeHolderList[1]" 
		""
		5 3 "Bruce01_RN" "|Bruce01_:Bruce01|Bruce01_:pCube1|Bruce01_:pCubeShape1.instObjGroups" 
		"Bruce01_RN.placeHolderList[2]" ":initialShadingGroup.dsm"
		5 3 "Bruce01_RN" "Bruce01_:Bruce01_AlembicNode.message" "Bruce01_RN.placeHolderList[3]" 
		""
		5 1 "Bruce01_RN" "|Bruce01_:Bruce01|Bruce01_:pCube1|Bruce01_:pCubeShape1.instObjGroups" 
		"Bruce01_RN.placeHolderList[4]" ":initialShadingGroup.dsm";
lockNode -l 1 ;
createNode objectSet -n "Bruce01_:Bruce01_CON";
	rename -uid "8435FCF7-4A3D-7454-29D7-2D9FB2FD4085";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "loader" -ln "loader" -dt "string";
	addAttr -ci true -sn "families" -ln "families" -dt "string";
	addAttr -ci true -sn "time" -ln "time" -dt "string";
	addAttr -ci true -sn "version" -ln "version" -dt "string";
	addAttr -ci true -sn "path" -ln "path" -dt "string";
	addAttr -ci true -sn "source" -ln "source" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 3 ".dsm";
	setAttr -s 2 ".dnsm";
	setAttr ".id" -type "string" "pyblish.mindbender.container";
	setAttr ".author" -type "string" "marcus";
	setAttr ".loader" -type "string" "mindbender.maya.pipeline";
	setAttr ".families" -type "string" "mindbender.animation";
	setAttr ".time" -type "string" "20170116T144405Z";
	setAttr ".version" -type "string" "2";
	setAttr ".path" -type "string" "{root}\\film\\1000\\publish\\Bruce01\\v002";
	setAttr ".source" -type "string" "{root}\\film\\1000\\work\\animation\\marcus\\maya\\scenes\\animation_v001.ma";
createNode reference -n "Bruce02_RN";
	rename -uid "4F32555F-41CF-3A53-FFD8-D689440B4CD4";
	setAttr -s 4 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"Bruce02_RN"
		"Bruce02_RN" 0
		"Bruce02_RN" 5
		3 "|Bruce02_:Bruce02|Bruce02_:pCube1|Bruce02_:pCubeShape1.instObjGroups" 
		":initialShadingGroup.dagSetMembers" "-na"
		5 3 "Bruce02_RN" "|Bruce02_:Bruce02|Bruce02_:pCube1.instObjGroups" "Bruce02_RN.placeHolderList[1]" 
		""
		5 3 "Bruce02_RN" "|Bruce02_:Bruce02|Bruce02_:pCube1|Bruce02_:pCubeShape1.instObjGroups" 
		"Bruce02_RN.placeHolderList[2]" ":initialShadingGroup.dsm"
		5 3 "Bruce02_RN" "Bruce02_:Bruce02_AlembicNode.message" "Bruce02_RN.placeHolderList[3]" 
		""
		5 1 "Bruce02_RN" "|Bruce02_:Bruce02|Bruce02_:pCube1|Bruce02_:pCubeShape1.instObjGroups" 
		"Bruce02_RN.placeHolderList[4]" ":initialShadingGroup.dsm";
lockNode -l 1 ;
createNode objectSet -n "Bruce02_:Bruce02_CON";
	rename -uid "25C4CE35-450B-8675-6314-5F924ECD2219";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "loader" -ln "loader" -dt "string";
	addAttr -ci true -sn "families" -ln "families" -dt "string";
	addAttr -ci true -sn "time" -ln "time" -dt "string";
	addAttr -ci true -sn "version" -ln "version" -dt "string";
	addAttr -ci true -sn "path" -ln "path" -dt "string";
	addAttr -ci true -sn "source" -ln "source" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 3 ".dsm";
	setAttr -s 2 ".dnsm";
	setAttr ".id" -type "string" "pyblish.mindbender.container";
	setAttr ".author" -type "string" "marcus";
	setAttr ".loader" -type "string" "mindbender.maya.pipeline";
	setAttr ".families" -type "string" "mindbender.animation";
	setAttr ".time" -type "string" "20170116T144405Z";
	setAttr ".version" -type "string" "2";
	setAttr ".path" -type "string" "{root}\\film\\1000\\publish\\Bruce02\\v002";
	setAttr ".source" -type "string" "{root}\\film\\1000\\work\\animation\\marcus\\maya\\scenes\\animation_v001.ma";
createNode reference -n "Bruce_RN";
	rename -uid "AA95209B-4300-2F79-9406-E38A63F1B10B";
	setAttr -s 5 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".phl[5]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"Bruce_RN"
		"Bruce_RN" 0
		"Bruce_RN" 5
		5 3 "Bruce_RN" "Bruce_:blinn1SG.message" "Bruce_RN.placeHolderList[1]" 
		""
		5 2 "Bruce_RN" "Bruce_:blinn1SG.dagSetMembers" "Bruce_RN.placeHolderList[2]" 
		":initialShadingGroup.dsm"
		5 2 "Bruce_RN" "Bruce_:blinn1SG.dagSetMembers" "Bruce_RN.placeHolderList[3]" 
		":initialShadingGroup.dsm"
		5 3 "Bruce_RN" "Bruce_:materialInfo1.message" "Bruce_RN.placeHolderList[4]" 
		""
		5 3 "Bruce_RN" "Bruce_:blinn1.message" "Bruce_RN.placeHolderList[5]" 
		"";
lockNode -l 1 ;
createNode objectSet -n "Bruce_:lookdevDefault01_CON";
	rename -uid "E1AD5D10-4EFC-057C-7537-A8A80E4322B3";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "loader" -ln "loader" -dt "string";
	addAttr -ci true -sn "families" -ln "families" -dt "string";
	addAttr -ci true -sn "time" -ln "time" -dt "string";
	addAttr -ci true -sn "version" -ln "version" -dt "string";
	addAttr -ci true -sn "path" -ln "path" -dt "string";
	addAttr -ci true -sn "source" -ln "source" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 4 ".dnsm";
	setAttr ".id" -type "string" "pyblish.mindbender.container";
	setAttr ".author" -type "string" "marcus";
	setAttr ".loader" -type "string" "mindbender.maya.pipeline";
	setAttr ".families" -type "string" "mindbender.lookdev";
	setAttr ".time" -type "string" "20170116T143016Z";
	setAttr ".version" -type "string" "1";
	setAttr ".path" -type "string" "{root}\\assets\\Bruce\\publish\\lookdevDefault\\v001";
	setAttr ".source" -type "string" "{root}\\assets\\Bruce\\work\\lookdev\\marcus\\maya\\scenes\\lookdev_v001.ma";
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "20FDE9D3-4734-4745-91B8-C99EC11EBF76";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "507A82C3-4FDD-EF33-5D86-93A1E6415474";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -303.57141650858432 -188.09523062100519 ;
	setAttr ".tgi[0].vh" -type "double2" 303.57141650858432 188.09523062100519 ;
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
	setAttr -s 3 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 5 ".s";
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
connectAttr "Bruce01_RN.phl[1]" "Bruce01_:Bruce01_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[2]" "Bruce01_:Bruce01_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[3]" "Bruce01_:Bruce01_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[1]" "Bruce02_:Bruce02_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[2]" "Bruce02_:Bruce02_CON.dsm" -na;
connectAttr "Bruce02_RN.phl[3]" "Bruce02_:Bruce02_CON.dnsm" -na;
connectAttr "Bruce_RN.phl[1]" "Bruce_:lookdevDefault01_CON.dnsm" -na;
connectAttr "Bruce02_RN.phl[4]" "Bruce_RN.phl[2]";
connectAttr "Bruce01_RN.phl[4]" "Bruce_RN.phl[3]";
connectAttr "Bruce_RN.phl[4]" "Bruce_:lookdevDefault01_CON.dnsm" -na;
connectAttr "Bruce_RN.phl[5]" "Bruce_:lookdevDefault01_CON.dnsm" -na;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "Bruce01_:Bruce01.msg" "Bruce01_RN.asn[0]";
connectAttr "Bruce01_RN.msg" "Bruce01_:Bruce01_CON.dnsm" -na;
connectAttr "Bruce01_:Bruce01.iog" "Bruce01_:Bruce01_CON.dsm" -na;
connectAttr "Bruce02_:Bruce02.msg" "Bruce02_RN.asn[0]";
connectAttr "Bruce02_RN.msg" "Bruce02_:Bruce02_CON.dnsm" -na;
connectAttr "Bruce02_:Bruce02.iog" "Bruce02_:Bruce02_CON.dsm" -na;
connectAttr "Bruce_RN.msg" "Bruce_:lookdevDefault01_CON.dnsm" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of lighting_v001.ma
