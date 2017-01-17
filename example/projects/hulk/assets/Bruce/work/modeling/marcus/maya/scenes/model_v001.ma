//Maya ASCII 2016ff07 scene
//Name: model_v001.ma
//Last modified: Tue, Jan 17, 2017 04:16:55 PM
//Codeset: 1252
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "76C938E6-40FB-D33C-268A-AAB591959989";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 5.2781686589192462 0.82543652803580703 3.3238401963342192 ;
	setAttr ".r" -type "double3" -7.5383527296024564 57.800000000000097 -7.4608188248592686e-016 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "C56AAA7D-4862-2C19-8996-649DDD6FC47D";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 6.2919252621578607;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "C2668551-4A9D-C534-9738-67B0B536CB8B";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "AF1B6AC7-4994-7C99-8396-6CB47FB38BCE";
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
	rename -uid "B272EB06-4EB8-7B13-DD13-379DC0DDB519";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "49147070-476A-1C9D-36AB-1BB713768048";
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
	rename -uid "F77B4DFE-4C36-560D-A864-32BB47908F52";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "97E4323C-4CFA-9567-6BD4-BC8BE192B923";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "ROOT";
	rename -uid "25BBE5F1-4078-B36D-8975-9C9599D59440";
createNode transform -n "MESH" -p "ROOT";
	rename -uid "F076C22E-4061-3C3A-9E62-94AECF3E97FA";
	addAttr -ci true -k true -sn "isStatic" -ln "isStatic" -min 0 -max 1 -at "long";
	addAttr -ci true -sn "assetName" -ln "assetName" -dt "string";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".assetName" -type "string" "BRUCE";
createNode transform -n "BRUCE" -p "MESH";
	rename -uid "D50CFA4F-4DEB-B13D-A6F0-50BFEEE34FAC";
createNode transform -n "bruce_0" -p "BRUCE";
	rename -uid "6C5B3756-4F30-FF8F-5011-B7BA7BF80EB5";
	addAttr -ci true -sn "mb_oldName" -ln "mb_oldName" -dt "string";
	addAttr -ci true -sn "mbID" -ln "mbID" -dt "string";
	addAttr -ci true -sn "mb_hierarchyIndex" -ln "mb_hierarchyIndex" -at "long";
	addAttr -ci true -sn "mb_newName" -ln "mb_newName" -dt "string";
	addAttr -ci true -sn "mb_assetName" -ln "mb_assetName" -dt "string";
	setAttr ".mb_oldName" -type "string" "|ROOT|MESH|BRUCE|pCube1";
	setAttr ".mbID" -type "string" "32f151e2-1029-3e07-a750-5bb07e16c181";
	setAttr ".mb_newName" -type "string" "bruce_0";
	setAttr ".mb_assetName" -type "string" "bruce";
createNode mesh -n "bruce_Shape0" -p "bruce_0";
	rename -uid "BD169814-4645-7E55-4855-65ADFD33736D";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 39 ".uvst[0].uvsp[0:38]" -type "float2" 0.375 0 0.5 0 0.5
		 0.125 0.375 0.125 0.625 0 0.625 0.125 0.625 0.25 0.5 0.25 0.375 0.25 0.5 0.375 0.375
		 0.375 0.625 0.375 0.625 0.5 0.5 0.5 0.375 0.5 0.5 0.625 0.375 0.625 0.625 0.625 0.625
		 0.75 0.5 0.75 0.375 0.75 0.5 0.875 0.375 0.875 0.625 0.875 0.625 1 0.5 1 0.375 1
		 0.75 0 0.75 0.125 0.875 0 0.875 0.125 0.875 0.25 0.75 0.25 0.125 0 0.25 0 0.25 0.125
		 0.125 0.125 0.25 0.25 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 26 ".vt[0:25]"  -0.27777779 -0.27777779 0.27777779 0.27777779 -0.27777779 0.27777779
		 -0.27777779 0.27777779 0.27777779 0.27777779 0.27777779 0.27777779 -0.27777779 0.27777779 -0.27777779
		 0.27777779 0.27777779 -0.27777779 -0.27777779 -0.27777779 -0.27777779 0.27777779 -0.27777779 -0.27777779
		 0.375 0 0.375 0 0.375 0.375 -0.375 0.375 0 0.375 0.375 0 0 0.375 -0.375 -0.375 0 -0.375
		 0.375 0 -0.375 0 -0.375 -0.375 -0.375 -0.375 0 0.375 -0.375 0 0 -0.375 0.375 -0.375 0 0.375
		 0 0 0.5 0 0.5 0 0 0 -0.5 0 -0.5 0 0.5 0 0 -0.5 0 0;
	setAttr -s 48 ".ed[0:47]"  0 18 1 18 1 1 2 9 1 9 3 1 4 12 1 12 5 1 6 15 1
		 15 7 1 0 19 1 19 2 1 1 8 1 8 3 1 2 10 1 10 4 1 3 11 1 11 5 1 4 13 1 13 6 1 5 14 1
		 14 7 1 6 16 1 16 0 1 7 17 1 17 1 1 18 20 1 20 19 1 8 20 1 9 20 1 9 21 1 21 10 1 11 21 1
		 12 21 1 12 22 1 22 13 1 14 22 1 15 22 1 15 23 1 23 16 1 17 23 1 18 23 1 17 24 1 24 8 1
		 14 24 1 11 24 1 16 25 1 25 13 1 19 25 1 10 25 1;
	setAttr -s 24 -ch 96 ".fc[0:23]" -type "polyFaces" 
		f 4 0 24 25 -9
		mu 0 4 0 1 2 3
		f 4 1 10 26 -25
		mu 0 4 1 4 5 2
		f 4 -27 11 -4 27
		mu 0 4 2 5 6 7
		f 4 -26 -28 -3 -10
		mu 0 4 3 2 7 8
		f 4 2 28 29 -13
		mu 0 4 8 7 9 10
		f 4 3 14 30 -29
		mu 0 4 7 6 11 9
		f 4 -31 15 -6 31
		mu 0 4 9 11 12 13
		f 4 -30 -32 -5 -14
		mu 0 4 10 9 13 14
		f 4 4 32 33 -17
		mu 0 4 14 13 15 16
		f 4 5 18 34 -33
		mu 0 4 13 12 17 15
		f 4 -35 19 -8 35
		mu 0 4 15 17 18 19
		f 4 -34 -36 -7 -18
		mu 0 4 16 15 19 20
		f 4 6 36 37 -21
		mu 0 4 20 19 21 22
		f 4 7 22 38 -37
		mu 0 4 19 18 23 21
		f 4 -39 23 -2 39
		mu 0 4 21 23 24 25
		f 4 -38 -40 -1 -22
		mu 0 4 22 21 25 26
		f 4 -24 40 41 -11
		mu 0 4 4 27 28 5
		f 4 -23 -20 42 -41
		mu 0 4 27 29 30 28
		f 4 -43 -19 -16 43
		mu 0 4 28 30 31 32
		f 4 -42 -44 -15 -12
		mu 0 4 5 28 32 6
		f 4 20 44 45 17
		mu 0 4 33 34 35 36
		f 4 21 8 46 -45
		mu 0 4 34 0 3 35
		f 4 -47 9 12 47
		mu 0 4 35 3 8 37
		f 4 -46 -48 13 16
		mu 0 4 36 35 37 38;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
	setAttr ".vbc" no;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "A6921CDD-4B47-1FA9-5C0B-FE9022C805DA";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "EF614656-4624-0056-80FB-3FB055662F35";
createNode displayLayer -n "defaultLayer";
	rename -uid "A7225D60-41E7-0807-F17F-3C94683E08E3";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "FD569FFB-4A68-345B-CF86-FAB7F72A2260";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "36432759-4EF3-34F4-7001-DFB92308DE15";
	setAttr ".g" yes;
createNode objectSet -n "modelDefault_SET";
	rename -uid "3461B540-46BE-B83E-0CAD-5CB21A79DF1D";
	addAttr -ci true -sn "subset" -ln "subset" -dt "string";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "family" -ln "family" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	setAttr ".ihi" 0;
	setAttr ".subset" -type "string" "modelDefault";
	setAttr ".id" -type "string" "pyblish.mindbender.instance";
	setAttr ".family" -type "string" "mindbender.model";
	setAttr ".name" -type "string" "modelDefault";
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "1E1E3335-4A1E-ABC9-7926-AFB87C11D701";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "51F507E8-41FE-347D-B12B-DF841FDE2815";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -449.99998211860731 -202.38094433905616 ;
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
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
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
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "ROOT.iog" "modelDefault_SET.dsm" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "bruce_Shape0.iog" ":initialShadingGroup.dsm" -na;
// End of model_v001.ma
