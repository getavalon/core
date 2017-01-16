//Maya ASCII 2016ff07 scene
//Name: rigDefault.ma
//Last modified: Mon, Jan 16, 2017 01:02:49 PM
//Codeset: 1252
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -n "rig_GRP";
	rename -uid "79D26988-420E-3EEA-F385-088F7B264668";
createNode transform -n "implementation_GRP" -p "rig_GRP";
	rename -uid "51253F7C-46FD-80ED-6826-589B7E3F9EE5";
createNode transform -n "input_GRP" -p "implementation_GRP";
	rename -uid "9372A059-4C88-A009-A9D0-49B9BF315989";
	setAttr ".v" no;
createNode transform -n "Bruce01_:modelDefault" -p "input_GRP";
	rename -uid "4D29CC6B-4240-9C21-6F35-F99A911A2F55";
createNode transform -n "Bruce01_:model_GRP" -p "Bruce01_:modelDefault";
	rename -uid "AB56520C-4A63-6A2D-F69E-8F8779BE60F3";
createNode transform -n "Bruce01_:pCube1" -p "Bruce01_:model_GRP";
	rename -uid "91E05465-410C-A543-713F-3FB7EF115549";
createNode mesh -n "Bruce01_:pCubeShape1" -p "|rig_GRP|implementation_GRP|input_GRP|Bruce01_:modelDefault|Bruce01_:model_GRP|Bruce01_:pCube1";
	rename -uid "8EE2FD3F-4694-E7E2-2A48-108B832CA877";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 8 ".vt[0:7]"  -0.5 -0.5 0.5 0.5 -0.5 0.5 -0.5 0.5 0.5 0.5 0.5 0.5
		 -0.5 0.5 -0.5 0.5 0.5 -0.5 -0.5 -0.5 -0.5 0.5 -0.5 -0.5;
	setAttr -s 12 ".ed[0:11]"  0 1 0 2 3 0 4 5 0 6 7 0 0 2 0 1 3 0 2 4 0
		 3 5 0 4 6 0 5 7 0 6 0 0 7 1 0;
	setAttr -s 6 -ch 24 ".fc[0:5]" -type "polyFaces" 
		f 4 0 5 -2 -5
		mu 0 4 0 1 3 2
		f 4 1 7 -3 -7
		mu 0 4 2 3 5 4
		f 4 2 9 -4 -9
		mu 0 4 4 5 7 6
		f 4 3 11 -1 -11
		mu 0 4 6 7 9 8
		f 4 -12 -10 -8 -6
		mu 0 4 1 10 11 3
		f 4 10 4 6 8
		mu 0 4 12 0 2 13;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
	setAttr ".vbc" no;
createNode transform -n "skeleton_GRP" -p "implementation_GRP";
	rename -uid "3AB72C7A-4F85-3B4C-EF61-28ADB5B8B2B0";
	setAttr ".v" no;
createNode joint -n "joint1" -p "skeleton_GRP";
	rename -uid "E96C4837-4756-C1EC-BEEA-C69A0D98D1B9";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".uoc" 1;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".radi" 0.5;
createNode parentConstraint -n "joint1_parentConstraint1" -p "joint1";
	rename -uid "FD28639C-45E4-E1AF-C4C9-FF8C9A8C54CA";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "nurbsCircle1W0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "geometry_GRP" -p "implementation_GRP";
	rename -uid "18560D21-47C4-8464-89D4-C38016611C3B";
createNode transform -n "Bruce01_:pCube1" -p "geometry_GRP";
	rename -uid "F80E829E-454A-591B-0D5B-04AA41E3B988";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode mesh -n "Bruce01_:pCubeShape1" -p "|rig_GRP|implementation_GRP|geometry_GRP|Bruce01_:pCube1";
	rename -uid "F52F3166-4F22-79E8-A7FD-F0994633CA18";
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
	setAttr ".vcs" 2;
createNode mesh -n "pCubeShape1Orig" -p "|rig_GRP|implementation_GRP|geometry_GRP|Bruce01_:pCube1";
	rename -uid "6F8168A2-40FC-23F0-3E13-B7A80DBC4B86";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".vbc" no;
createNode transform -n "output_GRP" -p "implementation_GRP";
	rename -uid "673863E0-46AC-0F9F-D04C-D1BA6218BEC4";
	setAttr ".v" no;
createNode transform -n "geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1" -p "output_GRP";
	rename -uid "6DB38DE8-403C-AB76-3786-B4983B8F71E5";
createNode mesh -n "geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1" -p "geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1";
	rename -uid "B1146C3B-475D-3664-0DCA-7CBEDD7EF762";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".vbc" no;
createNode transform -n "interface_GRP" -p "rig_GRP";
	rename -uid "9D8AB9CE-4725-17C6-CE73-80B0AE27F783";
createNode transform -n "controls_GRP" -p "interface_GRP";
	rename -uid "D07A3D09-42F0-79BF-B205-8685E3C58EAE";
createNode transform -n "nurbsCircle1" -p "controls_GRP";
	rename -uid "DF263BF1-4C29-F033-F2B5-809EFC01EE31";
createNode nurbsCurve -n "nurbsCircleShape1" -p "nurbsCircle1";
	rename -uid "F3B80EFE-4676-580C-9C32-CEAA4BBC9F97";
	setAttr -k off ".v";
	setAttr ".tw" yes;
createNode objectSet -n "out_SET";
	rename -uid "EAA5E9E3-4D0A-57B4-4F23-77AE31896928";
	setAttr ".ihi" 0;
createNode objectSet -n "controls_SET";
	rename -uid "5CCC90D8-470C-A04C-70C0-92BCC3A5F805";
	setAttr ".ihi" 0;
createNode skinCluster -n "skinCluster1";
	rename -uid "78CBA516-4D10-9FC8-6AD1-60BCD5E607EA";
	setAttr -s 8 ".wl";
	setAttr ".wl[0].w[0]"  1;
	setAttr ".wl[1].w[0]"  1;
	setAttr ".wl[2].w[0]"  1;
	setAttr ".wl[3].w[0]"  1;
	setAttr ".wl[4].w[0]"  1;
	setAttr ".wl[5].w[0]"  1;
	setAttr ".wl[6].w[0]"  1;
	setAttr ".wl[7].w[0]"  1;
	setAttr ".pm[0]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 0 -0 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".dpf[0]"  4;
	setAttr ".mmi" yes;
	setAttr ".mi" 5;
	setAttr ".ucm" yes;
createNode dagPose -n "bindPose1";
	rename -uid "85AB7DE4-43BB-B32F-AF89-9EBCB3C3BD75";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".bp" yes;
createNode objectSet -n "skinCluster1Set";
	rename -uid "73798604-461F-8AD2-4446-E884267E7110";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "skinCluster1GroupId";
	rename -uid "4FB91903-4376-6990-4D66-EFAFEEA2423C";
	setAttr ".ihi" 0;
createNode groupParts -n "skinCluster1GroupParts";
	rename -uid "8333367A-45E5-653D-DFF1-2699D30A3103";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode transformGeometry -n "geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry";
	rename -uid "0CFD90EC-484E-9E46-AB0B-D895195C8CF4";
createNode makeNurbCircle -n "makeNurbCircle1";
	rename -uid "49AEF14F-48D5-3270-E478-38AD3A63039B";
	setAttr ".nr" -type "double3" 0 1 0 ;
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
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :ikSystem;
	setAttr -s 4 ".sol";
connectAttr "joint1_parentConstraint1.ctx" "joint1.tx";
connectAttr "joint1_parentConstraint1.cty" "joint1.ty";
connectAttr "joint1_parentConstraint1.ctz" "joint1.tz";
connectAttr "joint1_parentConstraint1.crx" "joint1.rx";
connectAttr "joint1_parentConstraint1.cry" "joint1.ry";
connectAttr "joint1_parentConstraint1.crz" "joint1.rz";
connectAttr "joint1.ro" "joint1_parentConstraint1.cro";
connectAttr "joint1.pim" "joint1_parentConstraint1.cpim";
connectAttr "joint1.rp" "joint1_parentConstraint1.crp";
connectAttr "joint1.rpt" "joint1_parentConstraint1.crt";
connectAttr "joint1.jo" "joint1_parentConstraint1.cjo";
connectAttr "nurbsCircle1.t" "joint1_parentConstraint1.tg[0].tt";
connectAttr "nurbsCircle1.rp" "joint1_parentConstraint1.tg[0].trp";
connectAttr "nurbsCircle1.rpt" "joint1_parentConstraint1.tg[0].trt";
connectAttr "nurbsCircle1.r" "joint1_parentConstraint1.tg[0].tr";
connectAttr "nurbsCircle1.ro" "joint1_parentConstraint1.tg[0].tro";
connectAttr "nurbsCircle1.s" "joint1_parentConstraint1.tg[0].ts";
connectAttr "nurbsCircle1.pm" "joint1_parentConstraint1.tg[0].tpm";
connectAttr "joint1_parentConstraint1.w0" "joint1_parentConstraint1.tg[0].tw";
connectAttr "skinCluster1.og[0]" "|rig_GRP|implementation_GRP|geometry_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.i"
		;
connectAttr "skinCluster1GroupId.id" "|rig_GRP|implementation_GRP|geometry_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.iog.og[0].gid"
		;
connectAttr "skinCluster1Set.mwc" "|rig_GRP|implementation_GRP|geometry_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.iog.og[0].gco"
		;
connectAttr "|rig_GRP|implementation_GRP|input_GRP|Bruce01_:modelDefault|Bruce01_:model_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.o" "pCubeShape1Orig.i"
		;
connectAttr "geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.og" "geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1.i"
		;
connectAttr "makeNurbCircle1.oc" "nurbsCircleShape1.cr";
connectAttr "geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.iog" "out_SET.dsm" -na
		;
connectAttr "nurbsCircle1.iog" "controls_SET.dsm" -na;
connectAttr "skinCluster1GroupParts.og" "skinCluster1.ip[0].ig";
connectAttr "skinCluster1GroupId.id" "skinCluster1.ip[0].gi";
connectAttr "bindPose1.msg" "skinCluster1.bp";
connectAttr "joint1.wm" "skinCluster1.ma[0]";
connectAttr "joint1.liw" "skinCluster1.lw[0]";
connectAttr "joint1.obcc" "skinCluster1.ifcl[0]";
connectAttr "joint1.msg" "bindPose1.m[0]";
connectAttr "bindPose1.w" "bindPose1.p[0]";
connectAttr "joint1.bps" "bindPose1.wm[0]";
connectAttr "skinCluster1GroupId.msg" "skinCluster1Set.gn" -na;
connectAttr "|rig_GRP|implementation_GRP|geometry_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.iog.og[0]" "skinCluster1Set.dsm"
		 -na;
connectAttr "skinCluster1.msg" "skinCluster1Set.ub[0]";
connectAttr "pCubeShape1Orig.w" "skinCluster1GroupParts.ig";
connectAttr "skinCluster1GroupId.id" "skinCluster1GroupParts.gi";
connectAttr "|rig_GRP|implementation_GRP|geometry_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.o" "geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.ig"
		;
connectAttr "|rig_GRP|implementation_GRP|geometry_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.wm" "geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.txf"
		;
connectAttr "|rig_GRP|implementation_GRP|input_GRP|Bruce01_:modelDefault|Bruce01_:model_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|rig_GRP|implementation_GRP|geometry_GRP|Bruce01_:pCube1|Bruce01_:pCubeShape1.iog" ":initialShadingGroup.dsm"
		 -na;
// End of rigDefault.ma
