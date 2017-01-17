//Maya ASCII 2016ff07 scene
//Name: anim_v001.ma
//Last modified: Tue, Jan 17, 2017 04:33:59 PM
//Codeset: 1252
file -rdi 1 -ns "Bruce01_" -rfn "Bruce01_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v001/rigDefault.ma";
file -r -ns "Bruce01_" -dr 1 -rfn "Bruce01_RN" -typ "mayaAscii" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/publish/rigDefault/v001/rigDefault.ma";
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "A92BAD4D-4005-6C05-7C06-3AAB53E96CAA";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 8.4363025988537359 4.5239219734757858 4.2985108737519626 ;
	setAttr ".r" -type "double3" -25.538352729602515 63.00000000000005 7.0057736522861114e-015 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "327F41E0-441B-AC09-E2F7-2B94E7DD4E17";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 10.493534547200326;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "068C1F8C-447A-A208-4E4B-D1B1C1DA8776";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "CDB86289-41AF-C3E7-A6EF-F9A4B02A949D";
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
	rename -uid "8210B89C-4C26-3F1F-CBA3-BC9427141E0B";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "DC5F3129-4D74-C4B8-F4BA-B6BC44006E34";
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
	rename -uid "6A09DF92-4156-C3B6-B619-9991F5D5A7FE";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "6D38A51E-40A1-8DEF-6F68-DAAF66C1732A";
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
	rename -uid "03EB4166-4091-5B2D-1E9C-AE9EB9095FE1";
	setAttr ".rp" -type "double3" 0 0 1.1102230246251565e-016 ;
	setAttr ".sp" -type "double3" 0 0 1.1102230246251565e-016 ;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "9B1F00B2-42D1-0C2F-1B21-AA8DC20AE664";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "6C386A1B-422D-E778-6C53-4C8896B3C3B8";
createNode displayLayer -n "defaultLayer";
	rename -uid "A5814859-405D-2AAB-A413-97996BD23DA4";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "80947471-4617-AAA7-3811-DE9992157084";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "C0F74B98-45CD-23A7-FF8B-77B74ED3EB86";
	setAttr ".g" yes;
createNode reference -n "Bruce01_RN";
	rename -uid "E027252E-4C08-2123-6DAC-B2AD490F7F1E";
	setAttr -s 38 ".phl";
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
	setAttr ".phl[15]" 0;
	setAttr ".phl[16]" 0;
	setAttr ".phl[17]" 0;
	setAttr ".phl[18]" 0;
	setAttr ".phl[19]" 0;
	setAttr ".phl[20]" 0;
	setAttr ".phl[21]" 0;
	setAttr ".phl[22]" 0;
	setAttr ".phl[23]" 0;
	setAttr ".phl[24]" 0;
	setAttr ".phl[25]" 0;
	setAttr ".phl[26]" 0;
	setAttr ".phl[27]" 0;
	setAttr ".phl[28]" 0;
	setAttr ".phl[29]" 0;
	setAttr ".phl[30]" 0;
	setAttr ".phl[31]" 0;
	setAttr ".phl[32]" 0;
	setAttr ".phl[33]" 0;
	setAttr ".phl[34]" 0;
	setAttr ".phl[35]" 0;
	setAttr ".phl[36]" 0;
	setAttr ".phl[37]" 0;
	setAttr ".phl[38]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"Bruce01_RN"
		"Bruce01_RN" 0
		"Bruce01_RN" 46
		2 "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL" "translate" 
		" -type \"double3\" 0 0 0"
		2 "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL" "translateX" 
		" -av"
		2 "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL" "translateY" 
		" -av"
		2 "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL" "translateZ" 
		" -av"
		2 "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL" "rotate" 
		" -type \"double3\" 0 0 0"
		2 "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL" "rotateX" 
		" -av"
		2 "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL" "rotateY" 
		" -av"
		2 "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL" "rotateZ" 
		" -av"
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT.instObjGroups" 
		"Bruce01_RN.placeHolderList[1]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH.instObjGroups" 
		"Bruce01_RN.placeHolderList[2]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:Bruce01_:modelDefault.instObjGroups" 
		"Bruce01_RN.placeHolderList[3]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:ROOT.instObjGroups" 
		"Bruce01_RN.placeHolderList[4]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:ROOT|Bruce01_:Bruce01_:MESH.instObjGroups" 
		"Bruce01_RN.placeHolderList[5]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:ROOT|Bruce01_:Bruce01_:MESH|Bruce01_:Bruce01_:BRUCE.instObjGroups" 
		"Bruce01_RN.placeHolderList[6]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:ROOT|Bruce01_:Bruce01_:MESH|Bruce01_:Bruce01_:BRUCE|Bruce01_:Bruce01_:bruce_0.instObjGroups" 
		"Bruce01_RN.placeHolderList[7]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:ROOT|Bruce01_:Bruce01_:MESH|Bruce01_:Bruce01_:BRUCE|Bruce01_:Bruce01_:bruce_0|Bruce01_:Bruce01_:bruce_Shape0.instObjGroups" 
		"Bruce01_RN.placeHolderList[8]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:skinning_PLY.instObjGroups" 
		"Bruce01_RN.placeHolderList[9]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:skinning_PLY|Bruce01_:skinning_PLYShape.instObjGroups" 
		"Bruce01_RN.placeHolderList[10]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:skinning_PLY|Bruce01_:skinning_PLYShapeOrig.instObjGroups" 
		"Bruce01_RN.placeHolderList[11]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:output_GRP.instObjGroups" 
		"Bruce01_RN.placeHolderList[12]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:output_GRP|Bruce01_:bruce_0.instObjGroups" 
		"Bruce01_RN.placeHolderList[13]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:output_GRP|Bruce01_:bruce_0.instObjGroups" 
		"Bruce01_RN.placeHolderList[14]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:MESH|Bruce01_:output_GRP|Bruce01_:bruce_0|Bruce01_:bruce_Shape0.instObjGroups" 
		"Bruce01_RN.placeHolderList[15]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA.instObjGroups" 
		"Bruce01_RN.placeHolderList[16]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL.translateX" 
		"Bruce01_RN.placeHolderList[17]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL.translateY" 
		"Bruce01_RN.placeHolderList[18]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL.translateZ" 
		"Bruce01_RN.placeHolderList[19]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL.rotateX" 
		"Bruce01_RN.placeHolderList[20]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL.rotateY" 
		"Bruce01_RN.placeHolderList[21]" ""
		5 4 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL.rotateZ" 
		"Bruce01_RN.placeHolderList[22]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL.instObjGroups" 
		"Bruce01_RN.placeHolderList[23]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:ball_CTL|Bruce01_:ball_CTLShape.instObjGroups" 
		"Bruce01_RN.placeHolderList[24]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:joint1.instObjGroups" 
		"Bruce01_RN.placeHolderList[25]" ""
		5 3 "Bruce01_RN" "|Bruce01_:rigDefault|Bruce01_:ROOT|Bruce01_:DATA|Bruce01_:joint1|Bruce01_:joint1_parentConstraint1.instObjGroups" 
		"Bruce01_RN.placeHolderList[26]" ""
		5 3 "Bruce01_RN" "Bruce01_:controls_SET.message" "Bruce01_RN.placeHolderList[27]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:out_SET.message" "Bruce01_RN.placeHolderList[28]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:skinCluster1GroupId.message" "Bruce01_RN.placeHolderList[29]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:skinCluster1Set.message" "Bruce01_RN.placeHolderList[30]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:skinCluster1.message" "Bruce01_RN.placeHolderList[31]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:bindPose1.message" "Bruce01_RN.placeHolderList[32]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:skinCluster1GroupParts.message" "Bruce01_RN.placeHolderList[33]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:tweak1.message" "Bruce01_RN.placeHolderList[34]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:tweakSet1.message" "Bruce01_RN.placeHolderList[35]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:groupId2.message" "Bruce01_RN.placeHolderList[36]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:groupParts2.message" "Bruce01_RN.placeHolderList[37]" 
		""
		5 3 "Bruce01_RN" "Bruce01_:makeNurbCircle1.message" "Bruce01_RN.placeHolderList[38]" 
		"";
lockNode -l 1 ;
createNode objectSet -n "Bruce01_:rigDefault_CON";
	rename -uid "5083BCDE-467B-EC8D-20D2-81BB005E0AB7";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "loader" -ln "loader" -dt "string";
	addAttr -ci true -sn "families" -ln "families" -dt "string";
	addAttr -ci true -sn "time" -ln "time" -dt "string";
	addAttr -ci true -sn "version" -ln "version" -dt "string";
	addAttr -ci true -sn "path" -ln "path" -dt "string";
	addAttr -ci true -sn "source" -ln "source" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 20 ".dsm";
	setAttr -s 13 ".dnsm";
	setAttr ".id" -type "string" "pyblish.mindbender.container";
	setAttr ".author" -type "string" "marcus";
	setAttr ".loader" -type "string" "mindbender.maya.pipeline";
	setAttr ".families" -type "string" "mindbender.rig";
	setAttr ".time" -type "string" "20170117T163247Z";
	setAttr ".version" -type "string" "1";
	setAttr ".path" -type "string" "{root}\\assets\\Bruce\\publish\\rigDefault\\v001";
	setAttr ".source" -type "string" "{root}\\assets\\Bruce\\work\\rigging\\marcus\\maya\\scenes\\rig_v001.ma";
createNode objectSet -n "Bruce01_SET";
	rename -uid "54DB83AC-453A-1CA7-CB89-648D4E555595";
	addAttr -ci true -sn "subset" -ln "subset" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	addAttr -ci true -sn "family" -ln "family" -dt "string";
	addAttr -ci true -sn "startFrame" -ln "startFrame" -dt "string";
	addAttr -ci true -sn "endFrame" -ln "endFrame" -dt "string";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	setAttr ".ihi" 0;
	setAttr ".subset" -type "string" "Bruce01";
	setAttr ".name" -type "string" "Bruce01";
	setAttr ".family" -type "string" "mindbender.animation";
	setAttr ".startFrame" -type "string" "1.0";
	setAttr ".endFrame" -type "string" "48.0";
	setAttr ".id" -type "string" "pyblish.mindbender.instance";
createNode animCurveTL -n "ball_CTL_translateX";
	rename -uid "CE5D9119-4DDE-9A00-E88E-EB9EED4DC158";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 1.1743595013352666;
createNode animCurveTL -n "ball_CTL_translateY";
	rename -uid "96C65E8E-4E94-5794-4DF9-2BBBB62F74BA";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 0.9522742745642514;
createNode animCurveTL -n "ball_CTL_translateZ";
	rename -uid "19502028-4436-B2D9-DC36-9F9E9C6DB2E2";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 -1.8232897397854471;
createNode animCurveTA -n "ball_CTL_rotateX";
	rename -uid "97DC39F9-4F7E-DEFB-AE41-B893A1449E28";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 7.2077470515689273;
createNode animCurveTA -n "ball_CTL_rotateY";
	rename -uid "C15F2D7F-46A3-BD91-FDA6-5CB0990DACEE";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 19.517409278980253;
createNode animCurveTA -n "ball_CTL_rotateZ";
	rename -uid "A3D867E3-4A24-83BC-F926-2B85F412C141";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1 0 24 -103.61456105065473;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "B3247455-4CFF-76A4-7748-EEA5620D76A8";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "107E50E6-4D78-BBE2-DCB0-AE9F39C5076A";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -441.66664911641089 -228.57141948881642 ;
	setAttr ".tgi[0].vh" -type "double2" 376.19046124201037 228.57141948881642 ;
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
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr -s 3 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "Bruce01_RN.phl[1]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[2]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[3]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[4]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[5]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[6]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[7]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[8]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[9]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[10]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[11]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[12]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[13]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[14]" "Bruce01_SET.dsm" -na;
connectAttr "Bruce01_RN.phl[15]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[16]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "ball_CTL_translateX.o" "Bruce01_RN.phl[17]";
connectAttr "ball_CTL_translateY.o" "Bruce01_RN.phl[18]";
connectAttr "ball_CTL_translateZ.o" "Bruce01_RN.phl[19]";
connectAttr "ball_CTL_rotateX.o" "Bruce01_RN.phl[20]";
connectAttr "ball_CTL_rotateY.o" "Bruce01_RN.phl[21]";
connectAttr "ball_CTL_rotateZ.o" "Bruce01_RN.phl[22]";
connectAttr "Bruce01_RN.phl[23]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[24]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[25]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[26]" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.phl[27]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[28]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[29]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[30]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[31]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[32]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[33]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[34]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[35]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[36]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[37]" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.phl[38]" "Bruce01_:rigDefault_CON.dnsm" -na;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "Bruce01_:rigDefault.msg" "Bruce01_RN.asn[0]";
connectAttr "Bruce01_RN.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:rigDefault.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of anim_v001.ma
