//Maya ASCII 2015 scene
//Name: animation.ma
//Last modified: Tue, Sep 13, 2016 01:05:33 PM
//Codeset: ANSI_X3.4-1968
file -rdi 1 -ns "cube_" -rfn "cube_RN" -op "v=0;" "public/cube_rig/v001/cube_rig.ma";
file -r -ns "cube_" -dr 1 -rfn "cube_RN" -op "v=0;" "public/cube_rig/v001/cube_rig.ma";
requires maya "2015";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2015";
fileInfo "version" "2015";
fileInfo "cutIdentifier" "201410051530-933320";
fileInfo "osv" "Linux 2.6.32-573.26.1.el6.framestore.1.x86_64 #1 SMP Wed May 25 14:18:04 BST 2016 x86_64";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 40.766209175115691 14.83409866977102 -10.037287400019965 ;
	setAttr ".r" -type "double3" -13.538352729603846 102.59999999999908 0 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 45.041731280854201;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 0 -6.1629758220391547e-33 1.1102230246251565e-16 ;
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
	setAttr ".t" -type "double3" 1.5137322873829238 5.2438645265282373 100.26125818310602 ;
createNode camera -s -n "frontShape" -p "front";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 34.88464862287011;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.54445502021487 4.1305469146738645 0.45425599910149073 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 52.992073445300328;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode lightLinker -s -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
createNode reference -n "cube_RN";
	setAttr ".fn[0]" -type "string" "/net/homes/mottosso/pythonpath/pyblish-starter/examples/maya//public/cube_rig/v001/cube_rig.ma";
	setAttr -s 4 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"cube_RN"
		"cube_RN" 0
		"cube_RN" 10
		2 "|cube_:cubeRig_GRP|cube_:interface_GRP|cube_:controls_GRP|cube_:cube_CTL" 
		"translate" " -type \"double3\" 0 6.33717334011733691 7.5573326724119454"
		2 "|cube_:cubeRig_GRP|cube_:interface_GRP|cube_:controls_GRP|cube_:cube_CTL" 
		"translateX" " -av"
		2 "|cube_:cubeRig_GRP|cube_:interface_GRP|cube_:controls_GRP|cube_:cube_CTL" 
		"translateY" " -av"
		2 "|cube_:cubeRig_GRP|cube_:interface_GRP|cube_:controls_GRP|cube_:cube_CTL" 
		"translateZ" " -av"
		2 "|cube_:cubeRig_GRP|cube_:interface_GRP|cube_:controls_GRP|cube_:cube_CTL" 
		"rotate" " -type \"double3\" 99.82323482881336929 0 0"
		2 "|cube_:cubeRig_GRP|cube_:interface_GRP|cube_:controls_GRP|cube_:cube_CTL" 
		"rotateX" " -av"
		5 3 "cube_RN" "|cube_:cubeRig_GRP|cube_:implementation_GRP|cube_:geometry_GRP|cube_:cube_:cube.instObjGroups" 
		"cube_RN.placeHolderList[1]" ""
		5 4 "cube_RN" "|cube_:cubeRig_GRP|cube_:interface_GRP|cube_:controls_GRP|cube_:cube_CTL.translateY" 
		"cube_RN.placeHolderList[2]" ""
		5 4 "cube_RN" "|cube_:cubeRig_GRP|cube_:interface_GRP|cube_:controls_GRP|cube_:cube_CTL.translateZ" 
		"cube_RN.placeHolderList[3]" ""
		5 4 "cube_RN" "|cube_:cubeRig_GRP|cube_:interface_GRP|cube_:controls_GRP|cube_:cube_CTL.rotateX" 
		"cube_RN.placeHolderList[4]" "";
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
createNode reference -n "sharedReferenceNode";
	setAttr ".ed" -type "dataReferenceEdits" 
		"sharedReferenceNode";
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1001 -max 1050 -ast 1001 -aet 1100 ";
	setAttr ".st" 6;
createNode animCurveTL -n "cube_CTL_translateY";
	setAttr ".tan" 1;
	setAttr -s 10 ".ktv[0:9]"  1001 6.3371733401173369 1008 0.375 1013 2.9359668133970303
		 1018 0.375 1022 1.4136560267540208 1026 0.375 1028 0.62650559154990937 1030 0.375 1032 0.43900362049565927
		 1033.5 0.375;
	setAttr -s 10 ".kit[6:9]"  9 1 9 1;
	setAttr -s 10 ".kot[6:9]"  9 1 9 1;
	setAttr -s 10 ".ktl[1:9]" no yes no yes no yes no yes yes;
	setAttr -s 10 ".kwl[0:9]" no no no no no no no no yes no;
	setAttr -s 10 ".kix[0:9]"  0.45474702119827271 0.13960769772529602 0.31559726595878601 0.13595488667488098 0.19397872686386108 0.1117759495973587 
		0.083332061767578125 0.064086556434631348 0.083332061767578125 0.063580624759197235;
	setAttr -s 10 ".kiy[0:9]"  0 -5.3310556411743164 0 -2.8011770248413086 0 -1.7134642601013184 0 -0.48432162404060364 0 -0.11398027837276459;
	setAttr -s 10 ".kox[0:9]"  0.45474702119827271 0.1504673957824707 0.31559726595878601 0.15413115918636322 0.19397872686386108 0.062718600034713745 
		0.08333587646484375 0.078495323657989502 0.0625 0.063580624759197235;
	setAttr -s 10 ".koy[0:9]"  0 3.9815554618835449 0 2.408205509185791 0 0.5902896523475647 0 0.1651255190372467 0 -0.11398028582334518;
createNode animCurveTL -n "cube_CTL_translateZ";
	setAttr ".tan" 2;
	setAttr -s 2 ".ktv[0:1]"  1001 7.5573326724119454 1039 -4.1271756277452045;
	setAttr -s 2 ".kit[1]"  3;
	setAttr -s 2 ".kot[1]"  3;
createNode animCurveTA -n "cube_CTL_rotateX";
	setAttr ".tan" 2;
	setAttr -s 8 ".ktv[0:7]"  1001 99.823234828813369 1008 17.745802243679137 1018 -456.20626282527934
		 1026 -178.77962316547689 1027 -205.38736334491207 1030 -184.12468477805703 1032 -186.5885701955707 1034 -177.34899987989465;
	setAttr -s 8 ".kit[1:7]"  1 1 2 2 2 2 2;
	setAttr -s 8 ".kot[1:7]"  1 1 2 2 2 2 2;
	setAttr -s 8 ".kix[1:7]"  0.29166793823242188 0.41666793823242188 0.33333206176757812 0.041667938232421875 0.125 0.083332061767578125 
		0.083332061767578125;
	setAttr -s 8 ".kiy[1:7]"  -1.4325214624404907 -8.2720241546630859 4.842008113861084 -0.46439266204833984 0.37110376358032227 -0.043002914637327194 
		0.16126091778278351;
	setAttr -s 8 ".kox[1:7]"  0.41666793823242188 0.33333206176757812 0.041667938232421875 0.125 0.083332061767578125 0.083332061767578125 
		1;
	setAttr -s 8 ".koy[1:7]"  -8.2720670700073242 5.2021570205688477 -0.46439266204833984 0.37110376358032227 -0.043002914637327194 0.16126091778278351 
		0;
createNode objectSet -n "cube_animation";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "family" -ln "family" -dt "string";
	setAttr ".ihi" 0;
	setAttr -k on ".id" -type "string" "pyblish.starter.instance";
	setAttr -k on ".family" -type "string" "starter.animation";
select -ne :time1;
	setAttr ".o" 1001;
	setAttr ".unw" 1001;
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
select -ne :defaultHardwareRenderGlobals;
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
connectAttr "cube_RN.phl[1]" "cube_animation.dsm" -na;
connectAttr "cube_CTL_translateY.o" "cube_RN.phl[2]";
connectAttr "cube_CTL_translateZ.o" "cube_RN.phl[3]";
connectAttr "cube_CTL_rotateX.o" "cube_RN.phl[4]";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "sharedReferenceNode.sr" "cube_RN.sr";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
dataStructure -fmt "raw" -as "name=externalContentTable:string=node:string=key:string=upath:uint32=upathcrc:string=rpath:string=roles";
applyMetadata -fmt "raw" -v "channel\nname externalContentTable\nstream\nname v1.0\nindexType numeric\nstructure externalContentTable\n0\n\"cube_RN\" \"\" \"public/cube_rig/v001/cube_rig.ma\" 2530859423 \"/net/homes/mottosso/pythonpath/pyblish-starter/examples/maya/public/cube_rig/v001/cube_rig.ma\" \"FileRef\"\nendStream\nendChannel\nendAssociations\n" 
		-scn;
// End of animation.ma
