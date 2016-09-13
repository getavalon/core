//Maya ASCII 2015 scene
//Name: rig.ma
//Last modified: Tue, Sep 13, 2016 11:56:45 AM
//Codeset: ANSI_X3.4-1968
file -rdi 1 -ns "cube_" -rfn "cube_RN" -op "v=0;" "public/cube_model/v001/cube_model.ma";
file -r -ns "cube_" -dr 1 -rfn "cube_RN" -op "v=0;" "public/cube_model/v001/cube_model.ma";
requires maya "2015";
requires -nodeType "decomposeMatrix" "matrixNodes" "1.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2015";
fileInfo "version" "2015";
fileInfo "cutIdentifier" "201410051530-933320";
fileInfo "osv" "Linux 2.6.32-573.26.1.el6.framestore.1.x86_64 #1 SMP Wed May 25 14:18:04 BST 2016 x86_64";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -4.1343189370034663 3.8977280562389716 4.3554100016240138 ;
	setAttr ".r" -type "double3" -32.738352729604081 -42.20000000000033 0 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999986;
	setAttr ".coi" 7.2681786797171855;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
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
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
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
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "cubeRig_GRP";
createNode transform -n "implementation_GRP" -p "cubeRig_GRP";
	setAttr ".v" no;
createNode transform -n "geometry_GRP" -p "implementation_GRP";
createNode transform -n "skeleton_GRP" -p "implementation_GRP";
createNode joint -n "joint1" -p "skeleton_GRP";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".v" no;
	setAttr ".uoc" 1;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".radi" 0.5;
createNode transform -n "interface_GRP" -p "cubeRig_GRP";
createNode transform -n "controls_GRP" -p "interface_GRP";
createNode transform -n "cube_CTL" -p "controls_GRP";
createNode nurbsCurve -n "cube_CTLShape" -p "cube_CTL";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".tw" yes;
createNode transform -n "preview_GRP" -p "interface_GRP";
createNode transform -n "cube_PLY" -p "preview_GRP";
createNode mesh -n "cubeShapeDeformed" -p "cube_PLY";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode fosterParent -n "cube_RNfosterParent1";
createNode mesh -n "cubeShapeDeformed" -p "cube_RNfosterParent1";
	setAttr -k off ".v";
	setAttr -s 2 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".vbc" no;
createNode lightLinker -s -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	setAttr ".pee" 1;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -329.76189165834455 -127.38094731928832 ;
	setAttr ".tgi[0].vh" -type "double2" 484.52379027056401 234.52380020467101 ;
createNode reference -n "cube_RN";
	setAttr ".fn[0]" -type "string" "/net/homes/mottosso/pythonpath/pyblish-starter/examples/maya//public/cube_model/v001/cube_model.ma";
	setAttr -s 2 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"cube_RN"
		"cube_RN" 0
		"cube_RN" 15
		0 "|cube_:cube" "|cubeRig_GRP|implementation_GRP|geometry_GRP" "-s -r "
		0 "|cube_RNfosterParent1|cubeShapeDeformed" "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" 
		"-s -r "
		2 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube|cube_:cubeShape" 
		"intermediateObject" " 1"
		2 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube|cube_:cubeShape" 
		"vertexColorSource" " 2"
		5 3 "cube_RN" "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube.instObjGroups" 
		"cube_RN.placeHolderList[1]" ""
		5 3 "cube_RN" "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube|cube_:cubeShape.worldMesh" 
		"cube_RN.placeHolderList[2]" ""
		8 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" "translateX"
		8 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" "translateY"
		8 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" "translateZ"
		8 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" "rotateX"
		8 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" "rotateY"
		8 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" "rotateZ"
		8 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" "scaleX"
		8 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" "scaleY"
		8 "|cubeRig_GRP|implementation_GRP|geometry_GRP|cube_:cube" "scaleZ";
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
createNode skinCluster -n "skinCluster1";
	setAttr -s 8 ".wl";
	setAttr ".wl[0].w[0]"  1;
	setAttr ".wl[1].w[0]"  1;
	setAttr ".wl[2].w[0]"  1;
	setAttr ".wl[3].w[0]"  1;
	setAttr ".wl[4].w[0]"  1;
	setAttr ".wl[5].w[0]"  1;
	setAttr ".wl[6].w[0]"  1;
	setAttr ".wl[7].w[0]"  1;
	setAttr ".pm[0]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".dpf[0]"  4;
	setAttr ".mmi" yes;
	setAttr ".mi" 5;
	setAttr ".ucm" yes;
createNode objectSet -n "skinCluster1Set";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "skinCluster1GroupId";
	setAttr ".ihi" 0;
createNode groupParts -n "skinCluster1GroupParts";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode dagPose -n "bindPose1";
	setAttr -s 2 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr -s 2 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr -s 2 ".m";
	setAttr -s 2 ".p";
	setAttr -s 2 ".g[0:1]" yes no;
	setAttr ".bp" yes;
createNode makeNurbCircle -n "makeNurbCircle1";
	setAttr ".nr" -type "double3" 0 1 0 ;
createNode decomposeMatrix -n "nurbsCircle1_decompose";
	setAttr ".os" -type "double3" 1 1 1 ;
createNode objectSet -n "cache_SEL";
	setAttr ".ihi" 0;
createNode objectSet -n "controls_SEL";
	setAttr ".ihi" 0;
createNode objectSet -n "cube_rig";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "family" -ln "family" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 3 ".dnsm";
	setAttr -k on ".id" -type "string" "pyblish.starter.instance";
	setAttr -k on ".family" -type "string" "starter.rig";
createNode reference -n "sharedReferenceNode";
	setAttr ".ed" -type "dataReferenceEdits" 
		"sharedReferenceNode";
createNode objectSet -n "resources_SEL";
	setAttr ".ihi" 0;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 2 ".s";
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
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :ikSystem;
	setAttr -s 4 ".sol";
connectAttr "cube_RN.phl[1]" "cache_SEL.dsm" -na;
connectAttr "cube_RN.phl[2]" "skinCluster1GroupParts.ig";
connectAttr "nurbsCircle1_decompose.ot" "joint1.t";
connectAttr "nurbsCircle1_decompose.or" "joint1.r";
connectAttr "nurbsCircle1_decompose.os" "joint1.s";
connectAttr "makeNurbCircle1.oc" "cube_CTLShape.cr";
connectAttr "|cube_RNfosterParent1|cubeShapeDeformed.o" "|cubeRig_GRP|interface_GRP|preview_GRP|cube_PLY|cubeShapeDeformed.i"
		;
connectAttr "skinCluster1GroupId.id" "|cube_RNfosterParent1|cubeShapeDeformed.iog.og[0].gid"
		;
connectAttr "skinCluster1Set.mwc" "|cube_RNfosterParent1|cubeShapeDeformed.iog.og[0].gco"
		;
connectAttr "skinCluster1.og[0]" "|cube_RNfosterParent1|cubeShapeDeformed.i";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "cube_RNfosterParent1.msg" "cube_RN.fp";
connectAttr "sharedReferenceNode.sr" "cube_RN.sr";
connectAttr "skinCluster1GroupParts.og" "skinCluster1.ip[0].ig";
connectAttr "skinCluster1GroupId.id" "skinCluster1.ip[0].gi";
connectAttr "bindPose1.msg" "skinCluster1.bp";
connectAttr "joint1.wm" "skinCluster1.ma[0]";
connectAttr "joint1.liw" "skinCluster1.lw[0]";
connectAttr "joint1.obcc" "skinCluster1.ifcl[0]";
connectAttr "skinCluster1GroupId.msg" "skinCluster1Set.gn" -na;
connectAttr "|cube_RNfosterParent1|cubeShapeDeformed.iog.og[0]" "skinCluster1Set.dsm"
		 -na;
connectAttr "skinCluster1.msg" "skinCluster1Set.ub[0]";
connectAttr "skinCluster1GroupId.id" "skinCluster1GroupParts.gi";
connectAttr "cubeRig_GRP.msg" "bindPose1.m[0]";
connectAttr "joint1.msg" "bindPose1.m[1]";
connectAttr "bindPose1.w" "bindPose1.p[0]";
connectAttr "bindPose1.m[0]" "bindPose1.p[1]";
connectAttr "joint1.bps" "bindPose1.wm[1]";
connectAttr "cube_CTL.wm" "nurbsCircle1_decompose.imat";
connectAttr "cube_CTL.iog" "controls_SEL.dsm" -na;
connectAttr "cubeRig_GRP.iog" "cube_rig.dsm" -na;
connectAttr "cache_SEL.msg" "cube_rig.dnsm" -na;
connectAttr "controls_SEL.msg" "cube_rig.dnsm" -na;
connectAttr "resources_SEL.msg" "cube_rig.dnsm" -na;
connectAttr "cube_RN.msg" "resources_SEL.dnsm" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "|cube_RNfosterParent1|cubeShapeDeformed.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|cubeRig_GRP|interface_GRP|preview_GRP|cube_PLY|cubeShapeDeformed.iog" ":initialShadingGroup.dsm"
		 -na;
dataStructure -fmt "raw" -as "name=externalContentTable:string=node:string=key:string=upath:uint32=upathcrc:string=rpath:string=roles";
applyMetadata -fmt "raw" -v "channel\nname externalContentTable\nstream\nname v1.0\nindexType numeric\nstructure externalContentTable\n0\n\"cube_RN\" \"\" \"public/cube_model/v001/cube_model.ma\" 3218790889 \"/net/homes/mottosso/pythonpath/pyblish-starter/examples/maya/public/cube_model/v001/cube_model.ma\" \"FileRef\"\nendStream\nendChannel\nendAssociations\n" 
		-scn;
// End of rig.ma
