//Maya ASCII 2016ff07 scene
//Name: lookdev_v001.ma
//Last modified: Mon, Jan 16, 2017 02:35:00 PM
//Codeset: 1252
file -rdi 1 -ns "Bruce01_" -rfn "Bruce01_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/modelDefault/v002/modelDefault.ma";
file -r -ns "Bruce01_" -dr 1 -rfn "Bruce01_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/modelDefault/v002/modelDefault.ma";
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "77E8F9F1-4A0B-FC7B-0F61-C5B2E0791C15";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -4.095114074024317 2.1794703630844725 2.5390783005124913 ;
	setAttr ".r" -type "double3" -24.338352729603308 -58.199999999999953 3.0178571985015455e-015 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "672135E8-4993-A09B-3A3C-05824E983D5F";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 5.2883805610949057;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "96460589-46E6-85A8-BD43-1FB7D64C2896";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "B2BC7DEE-43B0-0D35-F441-A488C384DA05";
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
	rename -uid "42AFCE16-45C7-86AA-EFA1-21A69EC727E8";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "4EBA2599-4A42-0874-B1A9-8E841FEE1130";
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
	rename -uid "A47EC9BF-4D42-83DF-05F8-14B7B49BA02F";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "78F4864B-46C4-C933-5E75-53A88406775C";
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
	rename -uid "319C8B32-4AC7-9690-73C3-84951F449D9E";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "52CF26E9-4AD4-C6AF-AA3D-BAB360512EB7";
	setAttr -s 3 ".lnk";
	setAttr -s 3 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "3C825263-4B37-8998-F165-60A90AFB6C30";
createNode displayLayer -n "defaultLayer";
	rename -uid "123C7CAA-4294-9546-2DC2-8CADCDC94A4C";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "83E1BAF3-4BE0-BC25-E042-4AB22B844C13";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "FF01E30D-4AF1-B5B6-9943-ECA5EF72DFD4";
	setAttr ".g" yes;
createNode reference -n "Bruce01_RN";
	rename -uid "0CE53357-42A9-BBE9-7E93-E4ABFF605273";
	setAttr -s 5 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".phl[5]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"Bruce01_RN"
		"Bruce01_RN" 0
		"Bruce01_RN" 6
		3 "|Bruce01_:modelDefault|Bruce01_:model_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.instObjGroups" 
		":initialShadingGroup.dagSetMembers" "-na"
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:model_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[1]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:model_GRP|Bruce01_:pCube1.instObjGroups" 
		"Bruce01_RN.placeHolderList[2]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:model_GRP|Bruce01_:pCube1.instObjGroups" 
		"Bruce01_RN.placeHolderList[3]" ""
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:model_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.instObjGroups" 
		"Bruce01_RN.placeHolderList[4]" ":initialShadingGroup.dsm"
		5 3 "Bruce01_RN" "|Bruce01_:modelDefault|Bruce01_:model_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.instObjGroups" 
		"Bruce01_RN.placeHolderList[5]" ":initialShadingGroup.dsm";
lockNode -l 1 ;
createNode objectSet -n "Bruce01_:modelDefault_CON";
	rename -uid "2ABFAF8C-419B-CBF0-2F53-B798129C2BE8";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "loader" -ln "loader" -dt "string";
	addAttr -ci true -sn "families" -ln "families" -dt "string";
	addAttr -ci true -sn "time" -ln "time" -dt "string";
	addAttr -ci true -sn "version" -ln "version" -dt "string";
	addAttr -ci true -sn "path" -ln "path" -dt "string";
	addAttr -ci true -sn "source" -ln "source" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 4 ".dsm";
	setAttr ".id" -type "string" "pyblish.mindbender.container";
	setAttr ".author" -type "string" "marcus";
	setAttr ".loader" -type "string" "mindbender.maya.pipeline";
	setAttr ".families" -type "string" "mindbender.model";
	setAttr ".time" -type "string" "20170116T142904Z";
	setAttr ".version" -type "string" "2";
	setAttr ".path" -type "string" "{root}\\assets\\Bruce\\publish\\modelDefault\\v002";
	setAttr ".source" -type "string" "{root}\\assets\\Bruce\\work\\modeling\\marcus\\maya\\scenes\\cube_v001.ma";
createNode objectSet -n "lookdevDefault_SET";
	rename -uid "FE486871-491B-05F7-B11B-55BA0A997331";
	addAttr -ci true -sn "subset" -ln "subset" -dt "string";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "family" -ln "family" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	setAttr ".ihi" 0;
	setAttr ".subset" -type "string" "lookdevDefault";
	setAttr ".id" -type "string" "pyblish.mindbender.instance";
	setAttr ".family" -type "string" "mindbender.lookdev";
	setAttr ".name" -type "string" "lookdevDefault";
createNode blinn -n "blinn1";
	rename -uid "792F42BC-4737-5110-97BC-A08000F8104B";
	setAttr ".c" -type "float3" 0.92673141 0.36500001 1 ;
createNode shadingEngine -n "blinn1SG";
	rename -uid "2C136EBB-4568-04F8-06C6-0EBAA53CC7B5";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo1";
	rename -uid "B5AFA7C9-44E7-E809-8CA1-C3B906C2A7FD";
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "9E4D20BC-4B0D-81B1-5845-73BBDD950942";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "D9F69AA2-48C0-6F51-A386-FFAC95BC300A";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -323.80951094248991 -214.28570577076545 ;
	setAttr ".tgi[0].vh" -type "double2" 323.80951094248991 213.09522962759445 ;
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
connectAttr "Bruce01_RN.phl[1]" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[2]" "lookdevDefault_SET.dsm" -na;
connectAttr "Bruce01_RN.phl[3]" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[4]" "blinn1SG.dsm" -na;
connectAttr "Bruce01_RN.phl[5]" "Bruce01_:modelDefault_CON.dsm" -na;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "blinn1SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "blinn1SG.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "Bruce01_:modelDefault.msg" "Bruce01_RN.asn[0]";
connectAttr "Bruce01_RN.msg" "Bruce01_:modelDefault_CON.dnsm" -na;
connectAttr "Bruce01_:modelDefault.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "blinn1.oc" "blinn1SG.ss";
connectAttr "blinn1SG.msg" "materialInfo1.sg";
connectAttr "blinn1.msg" "materialInfo1.m";
connectAttr "blinn1SG.pa" ":renderPartition.st" -na;
connectAttr "blinn1.msg" ":defaultShaderList1.s" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of lookdev_v001.ma
