//Maya ASCII 2016ff07 scene
//Name: source.ma
//Last modified: Tue, Jan 17, 2017 04:33:52 PM
//Codeset: 1252
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "exportedFrom" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/film/1000/work/animation/marcus/maya/scenes/anim_v001.ma";
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
createNode transform -n "Bruce01_:ROOT" -p "Bruce01_:rigDefault";
	rename -uid "56C1617B-4969-B71F-B29E-1CB7D47F8129";
createNode transform -n "Bruce01_:MESH" -p "Bruce01_:ROOT";
	rename -uid "945D4809-4D37-A4CF-92D5-B7B3E0D3E11C";
createNode transform -n "Bruce01_:Bruce01_:modelDefault" -p "Bruce01_:MESH";
	rename -uid "287C3EDE-4FF5-02B3-35D0-7F9BE7DF76DE";
	setAttr ".v" no;
createNode transform -n "Bruce01_:Bruce01_:ROOT" -p "Bruce01_:Bruce01_:modelDefault";
	rename -uid "25BBE5F1-4078-B36D-8975-9C9599D59440";
createNode transform -n "Bruce01_:Bruce01_:MESH" -p "Bruce01_:Bruce01_:ROOT";
	rename -uid "F076C22E-4061-3C3A-9E62-94AECF3E97FA";
	addAttr -ci true -k true -sn "isStatic" -ln "isStatic" -min 0 -max 1 -at "long";
	addAttr -ci true -sn "assetName" -ln "assetName" -dt "string";
	setAttr ".assetName" -type "string" "BRUCE";
createNode transform -n "Bruce01_:Bruce01_:BRUCE" -p "Bruce01_:Bruce01_:MESH";
	rename -uid "D50CFA4F-4DEB-B13D-A6F0-50BFEEE34FAC";
createNode transform -n "Bruce01_:Bruce01_:bruce_0" -p "Bruce01_:Bruce01_:BRUCE";
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
createNode mesh -n "Bruce01_:Bruce01_:bruce_Shape0" -p "Bruce01_:Bruce01_:bruce_0";
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
createNode transform -n "Bruce01_:skinning_PLY" -p "Bruce01_:MESH";
	rename -uid "52AF7A80-4BFF-0243-FCBB-42AE8951EBC1";
	addAttr -ci true -sn "mb_oldName" -ln "mb_oldName" -dt "string";
	addAttr -ci true -sn "mbID" -ln "mbID" -dt "string";
	addAttr -ci true -sn "mb_hierarchyIndex" -ln "mb_hierarchyIndex" -at "long";
	addAttr -ci true -sn "mb_newName" -ln "mb_newName" -dt "string";
	addAttr -ci true -sn "mb_assetName" -ln "mb_assetName" -dt "string";
	setAttr ".mb_oldName" -type "string" "|ROOT|MESH|BRUCE|pCube1";
	setAttr ".mbID" -type "string" "32f151e2-1029-3e07-a750-5bb07e16c181";
	setAttr ".mb_newName" -type "string" "bruce_0";
	setAttr ".mb_assetName" -type "string" "bruce";
createNode mesh -n "Bruce01_:skinning_PLYShape" -p "Bruce01_:skinning_PLY";
	rename -uid "FFB9290C-4BEA-1ED6-DDEB-A286ADB352F0";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".vbc" no;
	setAttr ".vcs" 2;
createNode mesh -n "Bruce01_:skinning_PLYShapeOrig" -p "Bruce01_:skinning_PLY";
	rename -uid "F258C837-44CF-AC52-68D2-04AFAC42A0AE";
	setAttr -k off ".v";
	setAttr ".io" yes;
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
createNode transform -n "Bruce01_:output_GRP" -p "Bruce01_:MESH";
	rename -uid "444E54BB-487F-1EE6-6B53-879D4427FABF";
	setAttr ".v" no;
createNode transform -n "Bruce01_:bruce_0" -p "Bruce01_:output_GRP";
	rename -uid "F09A8521-4A0C-821D-394B-D583731786F4";
	addAttr -ci true -sn "mb_oldName" -ln "mb_oldName" -dt "string";
	addAttr -ci true -sn "mbID" -ln "mbID" -dt "string";
	addAttr -ci true -sn "mb_hierarchyIndex" -ln "mb_hierarchyIndex" -at "long";
	addAttr -ci true -sn "mb_newName" -ln "mb_newName" -dt "string";
	addAttr -ci true -sn "mb_assetName" -ln "mb_assetName" -dt "string";
	setAttr ".mb_oldName" -type "string" "|ROOT|MESH|BRUCE|pCube1";
	setAttr ".mbID" -type "string" "32f151e2-1029-3e07-a750-5bb07e16c181";
	setAttr ".mb_newName" -type "string" "bruce_0";
	setAttr ".mb_assetName" -type "string" "bruce";
createNode mesh -n "Bruce01_:bruce_Shape0" -p "Bruce01_:bruce_0";
	rename -uid "BC5E6D9A-4B2A-0A2F-1516-1DA38D9434C3";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".vbc" no;
createNode transform -n "Bruce01_:DATA" -p "Bruce01_:ROOT";
	rename -uid "8F6EEEEC-4BD1-6D0A-383D-D8BAA5724705";
createNode transform -n "Bruce01_:ball_CTL" -p "Bruce01_:DATA";
	rename -uid "E6A7046A-45DC-F487-DBA3-BF8D5F52A3B7";
	setAttr ".t" -type "double3" 0 0 0 ;
	setAttr -av ".tx";
	setAttr -av ".ty";
	setAttr -av ".tz";
	setAttr ".r" -type "double3" 0 0 0 ;
	setAttr -av ".rx";
	setAttr -av ".ry";
	setAttr -av ".rz";
createNode nurbsCurve -n "Bruce01_:ball_CTLShape" -p "Bruce01_:ball_CTL";
	rename -uid "83F09C5C-449C-AE25-020D-579BC0BA702D";
	setAttr -k off ".v";
	setAttr ".tw" yes;
createNode joint -n "Bruce01_:joint1" -p "Bruce01_:DATA";
	rename -uid "112FDECA-4297-5189-1956-3DA63E45B5B4";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".uoc" 1;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".radi" 0.5;
createNode parentConstraint -n "Bruce01_:joint1_parentConstraint1" -p "Bruce01_:joint1";
	rename -uid "E7009902-4E4B-F040-E9B2-05AF7775CF0C";
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
	rename -uid "557D98E1-4C89-A813-08AC-669F39CFA8BD";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -441.66664911641089 -228.57141948881642 ;
	setAttr ".tgi[0].vh" -type "double2" 376.19046124201037 228.57141948881642 ;
createNode objectSet -n "Bruce01_:controls_SET";
	rename -uid "E7DEC269-4256-5812-5754-EDBFC70EF1D7";
	setAttr ".ihi" 0;
createNode objectSet -n "Bruce01_:out_SET";
	rename -uid "3F100B25-4BCC-8DD6-D808-C4B71306C3A5";
	setAttr ".ihi" 0;
createNode groupId -n "Bruce01_:skinCluster1GroupId";
	rename -uid "6C0B4942-4D36-11CF-61BB-7C875DC6B158";
	setAttr ".ihi" 0;
createNode objectSet -n "Bruce01_:skinCluster1Set";
	rename -uid "056BF190-4AD4-BEBB-E9FC-8AB2889ED9A0";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode skinCluster -n "Bruce01_:skinCluster1";
	rename -uid "916D9F4C-4D3C-5DD4-CBFD-9C87DEE80784";
	setAttr -s 26 ".wl";
	setAttr ".wl[0].w[0]"  1;
	setAttr ".wl[1].w[0]"  1;
	setAttr ".wl[2].w[0]"  1;
	setAttr ".wl[3].w[0]"  1;
	setAttr ".wl[4].w[0]"  1;
	setAttr ".wl[5].w[0]"  1;
	setAttr ".wl[6].w[0]"  1;
	setAttr ".wl[7].w[0]"  1;
	setAttr ".wl[8].w[0]"  1;
	setAttr ".wl[9].w[0]"  1;
	setAttr ".wl[10].w[0]"  1;
	setAttr ".wl[11].w[0]"  1;
	setAttr ".wl[12].w[0]"  1;
	setAttr ".wl[13].w[0]"  1;
	setAttr ".wl[14].w[0]"  1;
	setAttr ".wl[15].w[0]"  1;
	setAttr ".wl[16].w[0]"  1;
	setAttr ".wl[17].w[0]"  1;
	setAttr ".wl[18].w[0]"  1;
	setAttr ".wl[19].w[0]"  1;
	setAttr ".wl[20].w[0]"  1;
	setAttr ".wl[21].w[0]"  1;
	setAttr ".wl[22].w[0]"  1;
	setAttr ".wl[23].w[0]"  1;
	setAttr ".wl[24].w[0]"  1;
	setAttr ".wl[25].w[0]"  1;
	setAttr ".pm[0]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".dpf[0]"  4;
	setAttr ".mmi" yes;
	setAttr ".mi" 5;
	setAttr ".ucm" yes;
createNode dagPose -n "Bruce01_:bindPose1";
	rename -uid "EFD93CF8-48C0-4489-FD80-CE8C61BA6D56";
	setAttr -s 3 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".wm[1]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr -s 3 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr -s 3 ".m";
	setAttr -s 3 ".p";
	setAttr -s 3 ".g[0:2]" yes yes no;
	setAttr ".bp" yes;
createNode groupParts -n "Bruce01_:skinCluster1GroupParts";
	rename -uid "DF3EC96E-4502-579C-6F97-37AFCCAAB6B5";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode tweak -n "Bruce01_:tweak1";
	rename -uid "127CA147-4F63-7C45-BD56-A3B6C6ECE56D";
createNode objectSet -n "Bruce01_:tweakSet1";
	rename -uid "FDA3C507-491B-6433-F579-C88418A8A76C";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "Bruce01_:groupId2";
	rename -uid "67FDE88F-4A75-EFEF-25EB-63A21831A532";
	setAttr ".ihi" 0;
createNode groupParts -n "Bruce01_:groupParts2";
	rename -uid "C6D284AB-401D-219B-6AA2-228FC23CF3EE";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode makeNurbCircle -n "Bruce01_:makeNurbCircle1";
	rename -uid "C652AAB9-4478-2DF1-9254-9BA5B03F6E62";
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
	setAttr -s 3 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "Bruce01_:skinCluster1GroupId.id" "Bruce01_:skinning_PLYShape.iog.og[0].gid"
		;
connectAttr "Bruce01_:skinCluster1Set.mwc" "Bruce01_:skinning_PLYShape.iog.og[0].gco"
		;
connectAttr "Bruce01_:groupId2.id" "Bruce01_:skinning_PLYShape.iog.og[1].gid";
connectAttr "Bruce01_:tweakSet1.mwc" "Bruce01_:skinning_PLYShape.iog.og[1].gco";
connectAttr "Bruce01_:skinCluster1.og[0]" "Bruce01_:skinning_PLYShape.i";
connectAttr "Bruce01_:tweak1.vl[0].vt[0]" "Bruce01_:skinning_PLYShape.twl";
connectAttr "Bruce01_:skinning_PLYShape.o" "Bruce01_:bruce_Shape0.i";
connectAttr "ball_CTL_translateX.o" "Bruce01_:ball_CTL.tx";
connectAttr "ball_CTL_translateY.o" "Bruce01_:ball_CTL.ty";
connectAttr "ball_CTL_translateZ.o" "Bruce01_:ball_CTL.tz";
connectAttr "ball_CTL_rotateX.o" "Bruce01_:ball_CTL.rx";
connectAttr "ball_CTL_rotateY.o" "Bruce01_:ball_CTL.ry";
connectAttr "ball_CTL_rotateZ.o" "Bruce01_:ball_CTL.rz";
connectAttr "Bruce01_:makeNurbCircle1.oc" "Bruce01_:ball_CTLShape.cr";
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
connectAttr "Bruce01_:ball_CTL.t" "Bruce01_:joint1_parentConstraint1.tg[0].tt";
connectAttr "Bruce01_:ball_CTL.rp" "Bruce01_:joint1_parentConstraint1.tg[0].trp"
		;
connectAttr "Bruce01_:ball_CTL.rpt" "Bruce01_:joint1_parentConstraint1.tg[0].trt"
		;
connectAttr "Bruce01_:ball_CTL.r" "Bruce01_:joint1_parentConstraint1.tg[0].tr";
connectAttr "Bruce01_:ball_CTL.ro" "Bruce01_:joint1_parentConstraint1.tg[0].tro"
		;
connectAttr "Bruce01_:ball_CTL.s" "Bruce01_:joint1_parentConstraint1.tg[0].ts";
connectAttr "Bruce01_:ball_CTL.pm" "Bruce01_:joint1_parentConstraint1.tg[0].tpm"
		;
connectAttr "Bruce01_:joint1_parentConstraint1.w0" "Bruce01_:joint1_parentConstraint1.tg[0].tw"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "Bruce01_:rigDefault.msg" "Bruce01_RN.asn[0]";
connectAttr "Bruce01_:bindPose1.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:controls_SET.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:groupId2.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:groupParts2.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:makeNurbCircle1.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:out_SET.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:skinCluster1.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:skinCluster1GroupId.msg" "Bruce01_:rigDefault_CON.dnsm" -na
		;
connectAttr "Bruce01_:skinCluster1GroupParts.msg" "Bruce01_:rigDefault_CON.dnsm"
		 -na;
connectAttr "Bruce01_:skinCluster1Set.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:tweak1.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:tweakSet1.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_RN.msg" "Bruce01_:rigDefault_CON.dnsm" -na;
connectAttr "Bruce01_:rigDefault.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:ROOT.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:DATA.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:ball_CTL.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:ball_CTLShape.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:joint1.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:joint1_parentConstraint1.iog" "Bruce01_:rigDefault_CON.dsm"
		 -na;
connectAttr "Bruce01_:MESH.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:Bruce01_:modelDefault.iog" "Bruce01_:rigDefault_CON.dsm" -na
		;
connectAttr "Bruce01_:Bruce01_:ROOT.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:Bruce01_:MESH.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:Bruce01_:BRUCE.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:Bruce01_:bruce_0.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:Bruce01_:bruce_Shape0.iog" "Bruce01_:rigDefault_CON.dsm" -na
		;
connectAttr "Bruce01_:output_GRP.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:bruce_0.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:bruce_Shape0.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:skinning_PLY.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:skinning_PLYShape.iog" "Bruce01_:rigDefault_CON.dsm" -na;
connectAttr "Bruce01_:skinning_PLYShapeOrig.iog" "Bruce01_:rigDefault_CON.dsm" -na
		;
connectAttr "Bruce01_:bruce_0.iog" "Bruce01_SET.dsm" -na;
connectAttr "Bruce01_:ball_CTL.iog" "Bruce01_:controls_SET.dsm" -na;
connectAttr "Bruce01_:bruce_0.iog" "Bruce01_:out_SET.dsm" -na;
connectAttr "Bruce01_:skinCluster1GroupId.msg" "Bruce01_:skinCluster1Set.gn" -na
		;
connectAttr "Bruce01_:skinning_PLYShape.iog.og[0]" "Bruce01_:skinCluster1Set.dsm"
		 -na;
connectAttr "Bruce01_:skinCluster1.msg" "Bruce01_:skinCluster1Set.ub[0]";
connectAttr "Bruce01_:skinCluster1GroupParts.og" "Bruce01_:skinCluster1.ip[0].ig"
		;
connectAttr "Bruce01_:skinCluster1GroupId.id" "Bruce01_:skinCluster1.ip[0].gi";
connectAttr "Bruce01_:bindPose1.msg" "Bruce01_:skinCluster1.bp";
connectAttr "Bruce01_:joint1.wm" "Bruce01_:skinCluster1.ma[0]";
connectAttr "Bruce01_:joint1.liw" "Bruce01_:skinCluster1.lw[0]";
connectAttr "Bruce01_:joint1.obcc" "Bruce01_:skinCluster1.ifcl[0]";
connectAttr "Bruce01_:ROOT.msg" "Bruce01_:bindPose1.m[0]";
connectAttr "Bruce01_:DATA.msg" "Bruce01_:bindPose1.m[1]";
connectAttr "Bruce01_:joint1.msg" "Bruce01_:bindPose1.m[2]";
connectAttr "Bruce01_:bindPose1.w" "Bruce01_:bindPose1.p[0]";
connectAttr "Bruce01_:bindPose1.m[0]" "Bruce01_:bindPose1.p[1]";
connectAttr "Bruce01_:bindPose1.m[1]" "Bruce01_:bindPose1.p[2]";
connectAttr "Bruce01_:joint1.bps" "Bruce01_:bindPose1.wm[2]";
connectAttr "Bruce01_:tweak1.og[0]" "Bruce01_:skinCluster1GroupParts.ig";
connectAttr "Bruce01_:skinCluster1GroupId.id" "Bruce01_:skinCluster1GroupParts.gi"
		;
connectAttr "Bruce01_:groupParts2.og" "Bruce01_:tweak1.ip[0].ig";
connectAttr "Bruce01_:groupId2.id" "Bruce01_:tweak1.ip[0].gi";
connectAttr "Bruce01_:groupId2.msg" "Bruce01_:tweakSet1.gn" -na;
connectAttr "Bruce01_:skinning_PLYShape.iog.og[1]" "Bruce01_:tweakSet1.dsm" -na;
connectAttr "Bruce01_:tweak1.msg" "Bruce01_:tweakSet1.ub[0]";
connectAttr "Bruce01_:skinning_PLYShapeOrig.w" "Bruce01_:groupParts2.ig";
connectAttr "Bruce01_:groupId2.id" "Bruce01_:groupParts2.gi";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "Bruce01_:skinning_PLYShape.iog" ":initialShadingGroup.dsm" -na;
connectAttr "Bruce01_:bruce_Shape0.iog" ":initialShadingGroup.dsm" -na;
connectAttr "Bruce01_:Bruce01_:bruce_Shape0.iog" ":initialShadingGroup.dsm" -na;
// End of source.ma
