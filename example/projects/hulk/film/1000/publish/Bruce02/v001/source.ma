//Maya ASCII 2016ff07 scene
//Name: source.ma
//Last modified: Mon, Jan 16, 2017 02:15:02 PM
//Codeset: 1252
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "exportedFrom" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/film/1000/work/animation/marcus/maya/scenes/animation_v001.ma";
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "A64759E7-4E44-082E-A357-349746868BDB";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -18.9946234690861 6.0777466661656634 2.5750413458560466 ;
	setAttr ".r" -type "double3" -17.738352729604124 -80.200000000000244 9.3430586925148265e-015 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "5234E64C-4663-3172-5B6F-A29B12526997";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999986;
	setAttr ".coi" 19.88994721570505;
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
createNode transform -n "Bruce01_:rig_GRP" -p "Bruce01_:rigDefault";
	rename -uid "79D26988-420E-3EEA-F385-088F7B264668";
createNode transform -n "Bruce01_:implementation_GRP" -p "Bruce01_:rig_GRP";
	rename -uid "51253F7C-46FD-80ED-6826-589B7E3F9EE5";
createNode transform -n "Bruce01_:input_GRP" -p "Bruce01_:implementation_GRP";
	rename -uid "9372A059-4C88-A009-A9D0-49B9BF315989";
	setAttr ".v" no;
createNode transform -n "Bruce01_:Bruce01_:modelDefault" -p "Bruce01_:input_GRP";
	rename -uid "4D29CC6B-4240-9C21-6F35-F99A911A2F55";
createNode transform -n "Bruce01_:Bruce01_:model_GRP" -p "Bruce01_:Bruce01_:modelDefault";
	rename -uid "AB56520C-4A63-6A2D-F69E-8F8779BE60F3";
createNode transform -n "Bruce01_:Bruce01_:pCube1" -p "Bruce01_:Bruce01_:model_GRP";
	rename -uid "91E05465-410C-A543-713F-3FB7EF115549";
createNode mesh -n "Bruce01_:Bruce01_:pCubeShape1" -p "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:model_GRP|Bruce01_:Bruce01_:pCube1";
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
createNode transform -n "Bruce01_:skeleton_GRP" -p "Bruce01_:implementation_GRP";
	rename -uid "3AB72C7A-4F85-3B4C-EF61-28ADB5B8B2B0";
	setAttr ".v" no;
createNode joint -n "Bruce01_:joint1" -p "Bruce01_:skeleton_GRP";
	rename -uid "E96C4837-4756-C1EC-BEEA-C69A0D98D1B9";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".uoc" 1;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".radi" 0.5;
createNode parentConstraint -n "Bruce01_:joint1_parentConstraint1" -p "Bruce01_:joint1";
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
createNode transform -n "Bruce01_:geometry_GRP" -p "Bruce01_:implementation_GRP";
	rename -uid "18560D21-47C4-8464-89D4-C38016611C3B";
createNode transform -n "Bruce01_:Bruce01_:pCube1" -p "Bruce01_:geometry_GRP";
	rename -uid "F80E829E-454A-591B-0D5B-04AA41E3B988";
createNode mesh -n "Bruce01_:Bruce01_:pCubeShape1" -p "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1";
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
createNode mesh -n "Bruce01_:pCubeShape1Orig" -p "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1";
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
createNode transform -n "Bruce01_:output_GRP" -p "Bruce01_:implementation_GRP";
	rename -uid "673863E0-46AC-0F9F-D04C-D1BA6218BEC4";
	setAttr ".v" no;
createNode transform -n "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1" 
		-p "Bruce01_:output_GRP";
	rename -uid "6DB38DE8-403C-AB76-3786-B4983B8F71E5";
createNode mesh -n "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1" 
		-p "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1";
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
createNode transform -n "Bruce01_:interface_GRP" -p "Bruce01_:rig_GRP";
	rename -uid "9D8AB9CE-4725-17C6-CE73-80B0AE27F783";
createNode transform -n "Bruce01_:controls_GRP" -p "Bruce01_:interface_GRP";
	rename -uid "D07A3D09-42F0-79BF-B205-8685E3C58EAE";
createNode transform -n "Bruce01_:nurbsCircle1" -p "Bruce01_:controls_GRP";
	rename -uid "DF263BF1-4C29-F033-F2B5-809EFC01EE31";
	setAttr ".t" -type "double3" 0 0 0 ;
	setAttr -av ".tx";
	setAttr -av ".ty";
	setAttr -av ".tz";
	setAttr ".r" -type "double3" 0 0 0 ;
	setAttr -av ".rx";
	setAttr -av ".ry";
	setAttr -av ".rz";
createNode nurbsCurve -n "Bruce01_:nurbsCircleShape1" -p "Bruce01_:nurbsCircle1";
	rename -uid "F3B80EFE-4676-580C-9C32-CEAA4BBC9F97";
	setAttr -k off ".v";
	setAttr ".tw" yes;
createNode transform -n "Bruce02_:rigDefault";
	rename -uid "736041AA-4E0E-FCA3-EFAB-E1AC0D281C0F";
	setAttr ".rp" -type "double3" 0 0 1.1102230246251565e-016 ;
	setAttr ".sp" -type "double3" 0 0 1.1102230246251565e-016 ;
createNode transform -n "Bruce02_:rig_GRP" -p "Bruce02_:rigDefault";
	rename -uid "79D26988-420E-3EEA-F385-088F7B264668";
createNode transform -n "Bruce02_:implementation_GRP" -p "Bruce02_:rig_GRP";
	rename -uid "51253F7C-46FD-80ED-6826-589B7E3F9EE5";
createNode transform -n "Bruce02_:input_GRP" -p "Bruce02_:implementation_GRP";
	rename -uid "9372A059-4C88-A009-A9D0-49B9BF315989";
	setAttr ".v" no;
createNode transform -n "Bruce02_:Bruce01_:modelDefault" -p "Bruce02_:input_GRP";
	rename -uid "4D29CC6B-4240-9C21-6F35-F99A911A2F55";
createNode transform -n "Bruce02_:Bruce01_:model_GRP" -p "Bruce02_:Bruce01_:modelDefault";
	rename -uid "AB56520C-4A63-6A2D-F69E-8F8779BE60F3";
createNode transform -n "Bruce02_:Bruce01_:pCube1" -p "Bruce02_:Bruce01_:model_GRP";
	rename -uid "91E05465-410C-A543-713F-3FB7EF115549";
createNode mesh -n "Bruce02_:Bruce01_:pCubeShape1" -p "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP|Bruce02_:Bruce01_:modelDefault|Bruce02_:Bruce01_:model_GRP|Bruce02_:Bruce01_:pCube1";
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
createNode transform -n "Bruce02_:skeleton_GRP" -p "Bruce02_:implementation_GRP";
	rename -uid "3AB72C7A-4F85-3B4C-EF61-28ADB5B8B2B0";
	setAttr ".v" no;
createNode joint -n "Bruce02_:joint1" -p "Bruce02_:skeleton_GRP";
	rename -uid "E96C4837-4756-C1EC-BEEA-C69A0D98D1B9";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".uoc" 1;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".radi" 0.5;
createNode parentConstraint -n "Bruce02_:joint1_parentConstraint1" -p "Bruce02_:joint1";
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
	setAttr ".lr" -type "double3" 25.885582126770188 56.155058763752102 -7.0891414851672865 ;
	setAttr -k on ".w0";
createNode transform -n "Bruce02_:geometry_GRP" -p "Bruce02_:implementation_GRP";
	rename -uid "18560D21-47C4-8464-89D4-C38016611C3B";
createNode transform -n "Bruce02_:Bruce01_:pCube1" -p "Bruce02_:geometry_GRP";
	rename -uid "F80E829E-454A-591B-0D5B-04AA41E3B988";
createNode mesh -n "Bruce02_:Bruce01_:pCubeShape1" -p "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1";
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
createNode mesh -n "Bruce02_:pCubeShape1Orig" -p "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1";
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
createNode transform -n "Bruce02_:output_GRP" -p "Bruce02_:implementation_GRP";
	rename -uid "673863E0-46AC-0F9F-D04C-D1BA6218BEC4";
	setAttr ".v" no;
createNode transform -n "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1" 
		-p "Bruce02_:output_GRP";
	rename -uid "6DB38DE8-403C-AB76-3786-B4983B8F71E5";
createNode mesh -n "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1" 
		-p "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1";
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
createNode transform -n "Bruce02_:interface_GRP" -p "Bruce02_:rig_GRP";
	rename -uid "9D8AB9CE-4725-17C6-CE73-80B0AE27F783";
createNode transform -n "Bruce02_:controls_GRP" -p "Bruce02_:interface_GRP";
	rename -uid "D07A3D09-42F0-79BF-B205-8685E3C58EAE";
createNode transform -n "Bruce02_:nurbsCircle1" -p "Bruce02_:controls_GRP";
	rename -uid "DF263BF1-4C29-F033-F2B5-809EFC01EE31";
	setAttr ".t" -type "double3" 0.70840795608917873 1.6142071819408139 0.18878114025646076 ;
	setAttr -av ".tx";
	setAttr -av ".ty";
	setAttr -av ".tz";
	setAttr ".r" -type "double3" 25.885582126770192 56.155058763752109 -7.0891414851672883 ;
	setAttr -av ".rx";
	setAttr -av ".ry";
	setAttr -av ".rz";
createNode nurbsCurve -n "Bruce02_:nurbsCircleShape1" -p "Bruce02_:nurbsCircle1";
	rename -uid "F3B80EFE-4676-580C-9C32-CEAA4BBC9F97";
	setAttr -k off ".v";
	setAttr ".tw" yes;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "9F63B6CC-4993-BF8C-8575-84911C02B687";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "7DB2EB9F-4939-C56E-F803-76B4EC45EC52";
createNode displayLayer -n "defaultLayer";
	rename -uid "B68707E8-4358-F470-B126-C88C68401C0B";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "45877637-42A6-9586-0CA6-F18E1197ACC4";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "76243CFE-44D3-1252-158D-5D8864D62AB9";
	setAttr ".g" yes;
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
	setAttr ".version" -type "string" "2";
	setAttr ".path" -type "string" "{root}\\assets\\Bruce\\publish\\rigDefault\\v002";
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
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "2AACB410-4724-9721-041F-2E87B2EF6BD2";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -320.2380825129772 -188.09523062100524 ;
	setAttr ".tgi[0].vh" -type "double2" 321.42855865614808 186.90475447783425 ;
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
	setAttr ".version" -type "string" "2";
	setAttr ".path" -type "string" "{root}\\assets\\Bruce\\publish\\rigDefault\\v002";
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
createNode objectSet -n "Bruce01_:out_SET";
	rename -uid "EAA5E9E3-4D0A-57B4-4F23-77AE31896928";
	setAttr ".ihi" 0;
createNode objectSet -n "Bruce01_:controls_SET";
	rename -uid "5CCC90D8-470C-A04C-70C0-92BCC3A5F805";
	setAttr ".ihi" 0;
createNode skinCluster -n "Bruce01_:skinCluster1";
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
	setAttr ".pm[0]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".dpf[0]"  4;
	setAttr ".mmi" yes;
	setAttr ".mi" 5;
	setAttr ".ucm" yes;
createNode dagPose -n "Bruce01_:bindPose1";
	rename -uid "85AB7DE4-43BB-B32F-AF89-9EBCB3C3BD75";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".bp" yes;
createNode objectSet -n "Bruce01_:skinCluster1Set";
	rename -uid "73798604-461F-8AD2-4446-E884267E7110";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Bruce01_:skinCluster1GroupId";
	rename -uid "4FB91903-4376-6990-4D66-EFAFEEA2423C";
	setAttr ".ihi" 0;
createNode groupParts -n "Bruce01_:skinCluster1GroupParts";
	rename -uid "8333367A-45E5-653D-DFF1-2699D30A3103";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode transformGeometry -n "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry";
	rename -uid "0CFD90EC-484E-9E46-AB0B-D895195C8CF4";
createNode makeNurbCircle -n "Bruce01_:makeNurbCircle1";
	rename -uid "49AEF14F-48D5-3270-E478-38AD3A63039B";
	setAttr ".nr" -type "double3" 0 1 0 ;
createNode objectSet -n "Bruce02_:out_SET";
	rename -uid "EAA5E9E3-4D0A-57B4-4F23-77AE31896928";
	setAttr ".ihi" 0;
createNode objectSet -n "Bruce02_:controls_SET";
	rename -uid "5CCC90D8-470C-A04C-70C0-92BCC3A5F805";
	setAttr ".ihi" 0;
createNode skinCluster -n "Bruce02_:skinCluster1";
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
	setAttr ".pm[0]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".dpf[0]"  4;
	setAttr ".mmi" yes;
	setAttr ".mi" 5;
	setAttr ".ucm" yes;
createNode dagPose -n "Bruce02_:bindPose1";
	rename -uid "85AB7DE4-43BB-B32F-AF89-9EBCB3C3BD75";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".bp" yes;
createNode objectSet -n "Bruce02_:skinCluster1Set";
	rename -uid "73798604-461F-8AD2-4446-E884267E7110";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Bruce02_:skinCluster1GroupId";
	rename -uid "4FB91903-4376-6990-4D66-EFAFEEA2423C";
	setAttr ".ihi" 0;
createNode groupParts -n "Bruce02_:skinCluster1GroupParts";
	rename -uid "8333367A-45E5-653D-DFF1-2699D30A3103";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode transformGeometry -n "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry";
	rename -uid "0CFD90EC-484E-9E46-AB0B-D895195C8CF4";
createNode makeNurbCircle -n "Bruce02_:makeNurbCircle1";
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
	setAttr -s 4 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "Bruce01_:joint1_parentConstraint1.ctx" "Bruce01_:joint1.tx";
connectAttr "Bruce01_:joint1_parentConstraint1.cty" "Bruce01_:joint1.ty";
connectAttr "Bruce01_:joint1_parentConstraint1.ctz" "Bruce01_:joint1.tz";
connectAttr "Bruce01_:joint1_parentConstraint1.crx" "Bruce01_:joint1.rx";
connectAttr "Bruce01_:joint1_parentConstraint1.cry" "Bruce01_:joint1.ry";
connectAttr "Bruce01_:joint1_parentConstraint1.crz" "Bruce01_:joint1.rz";
connectAttr "Bruce01_:joint1.ro" "Bruce01_:joint1_parentConstraint1.cro";
connectAttr "Bruce01_:joint1.pim" "Bruce01_:joint1_parentConstraint1.cpim";
connectAttr "Bruce01_:joint1.rp" "Bruce01_:joint1_parentConstraint1.crp";
connectAttr "Bruce01_:joint1.rpt" "Bruce01_:joint1_parentConstraint1.crt";
connectAttr "Bruce01_:joint1.jo" "Bruce01_:joint1_parentConstraint1.cjo";
connectAttr "Bruce01_:nurbsCircle1.t" "Bruce01_:joint1_parentConstraint1.tg[0].tt"
		;
connectAttr "Bruce01_:nurbsCircle1.rp" "Bruce01_:joint1_parentConstraint1.tg[0].trp"
		;
connectAttr "Bruce01_:nurbsCircle1.rpt" "Bruce01_:joint1_parentConstraint1.tg[0].trt"
		;
connectAttr "Bruce01_:nurbsCircle1.r" "Bruce01_:joint1_parentConstraint1.tg[0].tr"
		;
connectAttr "Bruce01_:nurbsCircle1.ro" "Bruce01_:joint1_parentConstraint1.tg[0].tro"
		;
connectAttr "Bruce01_:nurbsCircle1.s" "Bruce01_:joint1_parentConstraint1.tg[0].ts"
		;
connectAttr "Bruce01_:nurbsCircle1.pm" "Bruce01_:joint1_parentConstraint1.tg[0].tpm"
		;
connectAttr "Bruce01_:joint1_parentConstraint1.w0" "Bruce01_:joint1_parentConstraint1.tg[0].tw"
		;
connectAttr "Bruce01_:skinCluster1.og[0]" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.i"
		;
connectAttr "Bruce01_:skinCluster1GroupId.id" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.iog.og[0].gid"
		;
connectAttr "Bruce01_:skinCluster1Set.mwc" "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.iog.og[0].gco"
		;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:model_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.o" "Bruce01_:pCubeShape1Orig.i"
		;
connectAttr "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.og" "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1.i"
		;
connectAttr "nurbsCircle1_translateX.o" "Bruce01_:nurbsCircle1.tx";
connectAttr "nurbsCircle1_translateY.o" "Bruce01_:nurbsCircle1.ty";
connectAttr "nurbsCircle1_translateZ.o" "Bruce01_:nurbsCircle1.tz";
connectAttr "nurbsCircle1_rotateX.o" "Bruce01_:nurbsCircle1.rx";
connectAttr "nurbsCircle1_rotateY.o" "Bruce01_:nurbsCircle1.ry";
connectAttr "nurbsCircle1_rotateZ.o" "Bruce01_:nurbsCircle1.rz";
connectAttr "Bruce01_:makeNurbCircle1.oc" "Bruce01_:nurbsCircleShape1.cr";
connectAttr "Bruce02_:joint1_parentConstraint1.ctx" "Bruce02_:joint1.tx";
connectAttr "Bruce02_:joint1_parentConstraint1.cty" "Bruce02_:joint1.ty";
connectAttr "Bruce02_:joint1_parentConstraint1.ctz" "Bruce02_:joint1.tz";
connectAttr "Bruce02_:joint1_parentConstraint1.crx" "Bruce02_:joint1.rx";
connectAttr "Bruce02_:joint1_parentConstraint1.cry" "Bruce02_:joint1.ry";
connectAttr "Bruce02_:joint1_parentConstraint1.crz" "Bruce02_:joint1.rz";
connectAttr "Bruce02_:joint1.ro" "Bruce02_:joint1_parentConstraint1.cro";
connectAttr "Bruce02_:joint1.pim" "Bruce02_:joint1_parentConstraint1.cpim";
connectAttr "Bruce02_:joint1.rp" "Bruce02_:joint1_parentConstraint1.crp";
connectAttr "Bruce02_:joint1.rpt" "Bruce02_:joint1_parentConstraint1.crt";
connectAttr "Bruce02_:joint1.jo" "Bruce02_:joint1_parentConstraint1.cjo";
connectAttr "Bruce02_:nurbsCircle1.t" "Bruce02_:joint1_parentConstraint1.tg[0].tt"
		;
connectAttr "Bruce02_:nurbsCircle1.rp" "Bruce02_:joint1_parentConstraint1.tg[0].trp"
		;
connectAttr "Bruce02_:nurbsCircle1.rpt" "Bruce02_:joint1_parentConstraint1.tg[0].trt"
		;
connectAttr "Bruce02_:nurbsCircle1.r" "Bruce02_:joint1_parentConstraint1.tg[0].tr"
		;
connectAttr "Bruce02_:nurbsCircle1.ro" "Bruce02_:joint1_parentConstraint1.tg[0].tro"
		;
connectAttr "Bruce02_:nurbsCircle1.s" "Bruce02_:joint1_parentConstraint1.tg[0].ts"
		;
connectAttr "Bruce02_:nurbsCircle1.pm" "Bruce02_:joint1_parentConstraint1.tg[0].tpm"
		;
connectAttr "Bruce02_:joint1_parentConstraint1.w0" "Bruce02_:joint1_parentConstraint1.tg[0].tw"
		;
connectAttr "Bruce02_:skinCluster1.og[0]" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.i"
		;
connectAttr "Bruce02_:skinCluster1GroupId.id" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.iog.og[0].gid"
		;
connectAttr "Bruce02_:skinCluster1Set.mwc" "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.iog.og[0].gco"
		;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP|Bruce02_:Bruce01_:modelDefault|Bruce02_:Bruce01_:model_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.o" "Bruce02_:pCubeShape1Orig.i"
		;
connectAttr "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.og" "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1.i"
		;
connectAttr "nurbsCircle1_translateX1.o" "Bruce02_:nurbsCircle1.tx";
connectAttr "nurbsCircle1_translateY1.o" "Bruce02_:nurbsCircle1.ty";
connectAttr "nurbsCircle1_translateZ1.o" "Bruce02_:nurbsCircle1.tz";
connectAttr "nurbsCircle1_rotateX1.o" "Bruce02_:nurbsCircle1.rx";
connectAttr "nurbsCircle1_rotateY1.o" "Bruce02_:nurbsCircle1.ry";
connectAttr "nurbsCircle1_rotateZ1.o" "Bruce02_:nurbsCircle1.rz";
connectAttr "Bruce02_:makeNurbCircle1.oc" "Bruce02_:nurbsCircleShape1.cr";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "Bruce01_:rigDefault.msg" "Bruce01_RN.asn[0]";
connectAttr "Bruce01_:bindPose1.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:controls_SET.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.msg" "Bruce01_:rigDefault_CON.dnsm"
		 -na;
connectAttr "Bruce01_:makeNurbCircle1.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:out_SET.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:skinCluster1.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:skinCluster1GroupId.msg" "Bruce01_:rigDefault_CON.dnsm" -na
		;
connectAttr "Bruce01_:skinCluster1GroupParts.msg" "Bruce01_:rigDefault_CON.dnsm"
		 -na;
connectAttr "Bruce01_:skinCluster1Set.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:rigDefault.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:rig_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:implementation_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:geometry_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1.iog" "Bruce01_:rigDefault_CON.dsm"
		 -na;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.iog" "Bruce01_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce01_:pCubeShape1Orig.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:input_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:Bruce01_:modelDefault.iog" "Bruce01_:rigDefault_CON.dsm" -na
		;
connectAttr "Bruce01_:Bruce01_:model_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:model_GRP|Bruce01_:Bruce01_:pCube1.iog" "Bruce01_:rigDefault_CON.dsm"
		 -na;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:model_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.iog" "Bruce01_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce01_:output_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.iog" "Bruce01_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1.iog" "Bruce01_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce01_:skeleton_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:joint1.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:joint1_parentConstraint1.iog" "Bruce01_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce01_:interface_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:controls_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:nurbsCircle1.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:nurbsCircleShape1.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.iog" "Bruce01_SET.dsm"
		 -na;
connectAttr "Bruce02_:rigDefault.msg" "Bruce02_RN.asn[0]";
connectAttr "Bruce02_:bindPose1.msg" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_:controls_SET.msg" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.msg" "Bruce02_:rigDefault_CON.dnsm"
		 -na;
connectAttr "Bruce02_:makeNurbCircle1.msg" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_:out_SET.msg" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_:skinCluster1.msg" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_:skinCluster1GroupId.msg" "Bruce02_:rigDefault_CON.dnsm" -na
		;
connectAttr "Bruce02_:skinCluster1GroupParts.msg" "Bruce02_:rigDefault_CON.dnsm"
		 -na;
connectAttr "Bruce02_:skinCluster1Set.msg" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_RN.msg" "Bruce02_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce02_:rigDefault.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:rig_GRP.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:implementation_GRP.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:geometry_GRP.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1.iog" "Bruce02_:rigDefault_CON.dsm"
		 -na;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.iog" "Bruce02_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce02_:pCubeShape1Orig.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:input_GRP.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:Bruce01_:modelDefault.iog" "Bruce02_:rigDefault_CON.dsm" -na
		;
connectAttr "Bruce02_:Bruce01_:model_GRP.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP|Bruce02_:Bruce01_:modelDefault|Bruce02_:Bruce01_:model_GRP|Bruce02_:Bruce01_:pCube1.iog" "Bruce02_:rigDefault_CON.dsm"
		 -na;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP|Bruce02_:Bruce01_:modelDefault|Bruce02_:Bruce01_:model_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.iog" "Bruce02_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce02_:output_GRP.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.iog" "Bruce02_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCubeShape1.iog" "Bruce02_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce02_:skeleton_GRP.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:joint1.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:joint1_parentConstraint1.iog" "Bruce02_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce02_:interface_GRP.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:controls_GRP.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:nurbsCircle1.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:nurbsCircleShape1.iog" "Bruce02_:rigDefault_CON.dsm" -na;
connectAttr "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.iog" "Bruce02_SET.dsm"
		 -na;
connectAttr "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.iog" "Bruce01_:out_SET.dsm"
		 -na;
connectAttr "Bruce01_:nurbsCircle1.iog" "Bruce01_:controls_SET.dsm" -na;
connectAttr "Bruce01_:skinCluster1GroupParts.og" "Bruce01_:skinCluster1.ip[0].ig"
		;
connectAttr "Bruce01_:skinCluster1GroupId.id" "Bruce01_:skinCluster1.ip[0].gi";
connectAttr "Bruce01_:bindPose1.msg" "Bruce01_:skinCluster1.bp";
connectAttr "Bruce01_:joint1.wm" "Bruce01_:skinCluster1.ma[0]";
connectAttr "Bruce01_:joint1.liw" "Bruce01_:skinCluster1.lw[0]";
connectAttr "Bruce01_:joint1.obcc" "Bruce01_:skinCluster1.ifcl[0]";
connectAttr "Bruce01_:joint1.msg" "Bruce01_:bindPose1.m[0]";
connectAttr "Bruce01_:bindPose1.w" "Bruce01_:bindPose1.p[0]";
connectAttr "Bruce01_:joint1.bps" "Bruce01_:bindPose1.wm[0]";
connectAttr "Bruce01_:skinCluster1GroupId.msg" "Bruce01_:skinCluster1Set.gn" -na
		;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.iog.og[0]" "Bruce01_:skinCluster1Set.dsm"
		 -na;
connectAttr "Bruce01_:skinCluster1.msg" "Bruce01_:skinCluster1Set.ub[0]";
connectAttr "Bruce01_:pCubeShape1Orig.w" "Bruce01_:skinCluster1GroupParts.ig";
connectAttr "Bruce01_:skinCluster1GroupId.id" "Bruce01_:skinCluster1GroupParts.gi"
		;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.o" "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.ig"
		;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.wm" "Bruce01_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.txf"
		;
connectAttr "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_1:pCube1.iog" "Bruce02_:out_SET.dsm"
		 -na;
connectAttr "Bruce02_:nurbsCircle1.iog" "Bruce02_:controls_SET.dsm" -na;
connectAttr "Bruce02_:skinCluster1GroupParts.og" "Bruce02_:skinCluster1.ip[0].ig"
		;
connectAttr "Bruce02_:skinCluster1GroupId.id" "Bruce02_:skinCluster1.ip[0].gi";
connectAttr "Bruce02_:bindPose1.msg" "Bruce02_:skinCluster1.bp";
connectAttr "Bruce02_:joint1.wm" "Bruce02_:skinCluster1.ma[0]";
connectAttr "Bruce02_:joint1.liw" "Bruce02_:skinCluster1.lw[0]";
connectAttr "Bruce02_:joint1.obcc" "Bruce02_:skinCluster1.ifcl[0]";
connectAttr "Bruce02_:joint1.msg" "Bruce02_:bindPose1.m[0]";
connectAttr "Bruce02_:bindPose1.w" "Bruce02_:bindPose1.p[0]";
connectAttr "Bruce02_:joint1.bps" "Bruce02_:bindPose1.wm[0]";
connectAttr "Bruce02_:skinCluster1GroupId.msg" "Bruce02_:skinCluster1Set.gn" -na
		;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.iog.og[0]" "Bruce02_:skinCluster1Set.dsm"
		 -na;
connectAttr "Bruce02_:skinCluster1.msg" "Bruce02_:skinCluster1Set.ub[0]";
connectAttr "Bruce02_:pCubeShape1Orig.w" "Bruce02_:skinCluster1GroupParts.ig";
connectAttr "Bruce02_:skinCluster1GroupId.id" "Bruce02_:skinCluster1GroupParts.gi"
		;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.o" "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.ig"
		;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.wm" "Bruce02_:geometry_GRP_Bruce01_:pCube1_Bruce01_2:pCubeShape1_transformGeometry.txf"
		;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:input_GRP|Bruce01_:Bruce01_:modelDefault|Bruce01_:Bruce01_:model_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|Bruce01_:rigDefault|Bruce01_:rig_GRP|Bruce01_:implementation_GRP|Bruce01_:geometry_GRP|Bruce01_:Bruce01_:pCube1|Bruce01_:Bruce01_:pCubeShape1.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:input_GRP|Bruce02_:Bruce01_:modelDefault|Bruce02_:Bruce01_:model_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|Bruce02_:rigDefault|Bruce02_:rig_GRP|Bruce02_:implementation_GRP|Bruce02_:geometry_GRP|Bruce02_:Bruce01_:pCube1|Bruce02_:Bruce01_:pCubeShape1.iog" ":initialShadingGroup.dsm"
		 -na;
// End of source.ma
