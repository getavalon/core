//Maya ASCII 2016ff07 scene
//Name: source.ma
//Last modified: Tue, Jan 17, 2017 04:32:48 PM
//Codeset: 1252
requires maya "2016ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "exportedFrom" "C:/Users/marcus/Dropbox/AF/development/marcus/pyblish/pyblish-mindbender/example/projects/hulk/assets/Bruce/work/rigging/marcus/maya/scenes/rig_v001.ma";
fileInfo "application" "maya";
fileInfo "product" "Maya 2016";
fileInfo "version" "2016";
fileInfo "cutIdentifier" "201603180400-990260-1";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "F02E6190-453D-8497-1394-E9A7BF47E685";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -3.9671349981292456 2.9708373610042793 3.1669222625280082 ;
	setAttr ".r" -type "double3" -30.33835272960297 -51.399999999999842 -2.5490132216529781e-015 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "28C6FDBD-4519-E9E6-F021-11984869D707";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999986;
	setAttr ".coi" 5.8816180882318783;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "4DBDB7E1-4E7D-0541-6391-19AE1EA3143F";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "4F049DBA-469D-EF7B-489C-17A62C3273E9";
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
	rename -uid "5928C253-4741-178D-00BA-78ADF9C6C3C4";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "8795D5E1-4B0B-B454-9FAB-A4B75A130BDC";
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
	rename -uid "9740AD67-4108-AFD1-F01D-38B299569CD3";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "94877DF4-41C9-0E05-4387-72A00FAD43A6";
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
	rename -uid "56C1617B-4969-B71F-B29E-1CB7D47F8129";
createNode transform -n "MESH" -p "ROOT";
	rename -uid "945D4809-4D37-A4CF-92D5-B7B3E0D3E11C";
createNode transform -n "Bruce01_:modelDefault" -p "MESH";
	rename -uid "287C3EDE-4FF5-02B3-35D0-7F9BE7DF76DE";
	setAttr ".v" no;
createNode transform -n "Bruce01_:ROOT" -p "Bruce01_:modelDefault";
	rename -uid "25BBE5F1-4078-B36D-8975-9C9599D59440";
createNode transform -n "Bruce01_:MESH" -p "Bruce01_:ROOT";
	rename -uid "F076C22E-4061-3C3A-9E62-94AECF3E97FA";
	addAttr -ci true -k true -sn "isStatic" -ln "isStatic" -min 0 -max 1 -at "long";
	addAttr -ci true -sn "assetName" -ln "assetName" -dt "string";
	setAttr ".assetName" -type "string" "BRUCE";
createNode transform -n "Bruce01_:BRUCE" -p "Bruce01_:MESH";
	rename -uid "D50CFA4F-4DEB-B13D-A6F0-50BFEEE34FAC";
createNode transform -n "Bruce01_:bruce_0" -p "Bruce01_:BRUCE";
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
createNode mesh -n "Bruce01_:bruce_Shape0" -p "Bruce01_:bruce_0";
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
createNode transform -n "skinning_PLY" -p "MESH";
	rename -uid "52AF7A80-4BFF-0243-FCBB-42AE8951EBC1";
	addAttr -ci true -sn "mb_oldName" -ln "mb_oldName" -dt "string";
	addAttr -ci true -sn "mbID" -ln "mbID" -dt "string";
	addAttr -ci true -sn "mb_hierarchyIndex" -ln "mb_hierarchyIndex" -at "long";
	addAttr -ci true -sn "mb_newName" -ln "mb_newName" -dt "string";
	addAttr -ci true -sn "mb_assetName" -ln "mb_assetName" -dt "string";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".mb_oldName" -type "string" "|ROOT|MESH|BRUCE|pCube1";
	setAttr ".mbID" -type "string" "32f151e2-1029-3e07-a750-5bb07e16c181";
	setAttr ".mb_newName" -type "string" "bruce_0";
	setAttr ".mb_assetName" -type "string" "bruce";
createNode mesh -n "skinning_PLYShape" -p "skinning_PLY";
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
createNode mesh -n "skinning_PLYShapeOrig" -p "skinning_PLY";
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
createNode transform -n "output_GRP" -p "MESH";
	rename -uid "444E54BB-487F-1EE6-6B53-879D4427FABF";
	setAttr ".v" no;
createNode transform -n "bruce_0" -p "output_GRP";
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
createNode mesh -n "bruce_Shape0" -p "bruce_0";
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
createNode transform -n "DATA" -p "ROOT";
	rename -uid "8F6EEEEC-4BD1-6D0A-383D-D8BAA5724705";
createNode transform -n "ball_CTL" -p "DATA";
	rename -uid "E6A7046A-45DC-F487-DBA3-BF8D5F52A3B7";
createNode nurbsCurve -n "ball_CTLShape" -p "ball_CTL";
	rename -uid "83F09C5C-449C-AE25-020D-579BC0BA702D";
	setAttr -k off ".v";
	setAttr ".tw" yes;
createNode joint -n "joint1" -p "DATA";
	rename -uid "112FDECA-4297-5189-1956-3DA63E45B5B4";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".uoc" 1;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".radi" 0.5;
createNode parentConstraint -n "joint1_parentConstraint1" -p "joint1";
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
	rename -uid "3FFCB626-4DAA-40D3-9A14-519BCE6F6E5C";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "089FD61E-4461-DC4C-8B73-DFB8B0F0C361";
createNode displayLayer -n "defaultLayer";
	rename -uid "D3A8FF72-4928-2054-AB41-54AC700FDC46";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "D5093AE4-491C-DBA6-C3B1-0FBDCA481F35";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "16DACB43-475E-B867-815B-E1BFD8431766";
	setAttr ".g" yes;
createNode objectSet -n "Bruce01_:modelDefault_CON";
	rename -uid "B5B06E1B-4E49-2848-BFDB-66A637F13EAC";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "loader" -ln "loader" -dt "string";
	addAttr -ci true -sn "families" -ln "families" -dt "string";
	addAttr -ci true -sn "time" -ln "time" -dt "string";
	addAttr -ci true -sn "version" -ln "version" -dt "string";
	addAttr -ci true -sn "path" -ln "path" -dt "string";
	addAttr -ci true -sn "source" -ln "source" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 10 ".dsm";
	setAttr ".id" -type "string" "pyblish.mindbender.container";
	setAttr ".author" -type "string" "marcus";
	setAttr ".loader" -type "string" "mindbender.maya.pipeline";
	setAttr ".families" -type "string" "mindbender.model";
	setAttr ".time" -type "string" "20170117T161717Z";
	setAttr ".version" -type "string" "1";
	setAttr ".path" -type "string" "{root}\\assets\\Bruce\\publish\\modelDefault\\v001";
	setAttr ".source" -type "string" "{root}\\assets\\Bruce\\work\\modeling\\marcus\\maya\\scenes\\model_v001.ma";
createNode makeNurbCircle -n "makeNurbCircle1";
	rename -uid "C652AAB9-4478-2DF1-9254-9BA5B03F6E62";
	setAttr ".nr" -type "double3" 0 1 0 ;
createNode objectSet -n "controls_SET";
	rename -uid "E7DEC269-4256-5812-5754-EDBFC70EF1D7";
	setAttr ".ihi" 0;
createNode skinCluster -n "skinCluster1";
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
createNode tweak -n "tweak1";
	rename -uid "127CA147-4F63-7C45-BD56-A3B6C6ECE56D";
createNode objectSet -n "skinCluster1Set";
	rename -uid "056BF190-4AD4-BEBB-E9FC-8AB2889ED9A0";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "skinCluster1GroupId";
	rename -uid "6C0B4942-4D36-11CF-61BB-7C875DC6B158";
	setAttr ".ihi" 0;
createNode groupParts -n "skinCluster1GroupParts";
	rename -uid "DF3EC96E-4502-579C-6F97-37AFCCAAB6B5";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode objectSet -n "tweakSet1";
	rename -uid "FDA3C507-491B-6433-F579-C88418A8A76C";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "groupId2";
	rename -uid "67FDE88F-4A75-EFEF-25EB-63A21831A532";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts2";
	rename -uid "C6D284AB-401D-219B-6AA2-228FC23CF3EE";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode dagPose -n "bindPose1";
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
createNode objectSet -n "out_SET";
	rename -uid "3F100B25-4BCC-8DD6-D808-C4B71306C3A5";
	setAttr ".ihi" 0;
createNode objectSet -n "rigDefault_SET";
	rename -uid "19685007-4FFA-5168-9AF6-2AB50BE583D9";
	addAttr -ci true -sn "subset" -ln "subset" -dt "string";
	addAttr -ci true -sn "id" -ln "id" -dt "string";
	addAttr -ci true -sn "family" -ln "family" -dt "string";
	addAttr -ci true -sn "name" -ln "name" -dt "string";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dnsm";
	setAttr ".subset" -type "string" "rigDefault";
	setAttr ".id" -type "string" "pyblish.mindbender.instance";
	setAttr ".family" -type "string" "mindbender.rig";
	setAttr ".name" -type "string" "rigDefault";
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "C560DAD4-483F-832A-66C2-FF82DF5C31B8";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "8E6C7F34-45E2-997F-5ED7-1D85DFFCEBCB";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" 1081.4109975134502 -633.94136727402906 ;
	setAttr ".tgi[0].vh" -type "double2" 2110.45582827923 -151.96613025317939 ;
	setAttr -s 16 ".tgi[0].ni";
	setAttr ".tgi[0].ni[0].x" 1245.25390625;
	setAttr ".tgi[0].ni[0].y" -371.143310546875;
	setAttr ".tgi[0].ni[0].nvs" 18304;
	setAttr ".tgi[0].ni[1].x" 1047.142822265625;
	setAttr ".tgi[0].ni[1].y" -325.71429443359375;
	setAttr ".tgi[0].ni[1].nvs" 18304;
	setAttr ".tgi[0].ni[2].x" 1470.0272216796875;
	setAttr ".tgi[0].ni[2].y" -276.17388916015625;
	setAttr ".tgi[0].ni[2].nvs" 18304;
	setAttr ".tgi[0].ni[3].x" 262.85714721679687;
	setAttr ".tgi[0].ni[3].y" -455.71429443359375;
	setAttr ".tgi[0].ni[3].nvs" 18304;
	setAttr ".tgi[0].ni[4].x" 1667.9951171875;
	setAttr ".tgi[0].ni[4].y" -350.99270629882812;
	setAttr ".tgi[0].ni[4].nvs" 18304;
	setAttr ".tgi[0].ni[5].x" 524.28570556640625;
	setAttr ".tgi[0].ni[5].y" -232.85714721679687;
	setAttr ".tgi[0].ni[5].nvs" 18304;
	setAttr ".tgi[0].ni[6].x" 1604.2857666015625;
	setAttr ".tgi[0].ni[6].y" -184.28572082519531;
	setAttr ".tgi[0].ni[6].nvs" 18304;
	setAttr ".tgi[0].ni[7].x" 1604.2857666015625;
	setAttr ".tgi[0].ni[7].y" -597.14288330078125;
	setAttr ".tgi[0].ni[7].nvs" 18304;
	setAttr ".tgi[0].ni[8].x" 785.71429443359375;
	setAttr ".tgi[0].ni[8].y" -325.71429443359375;
	setAttr ".tgi[0].ni[8].nvs" 18304;
	setAttr ".tgi[0].ni[9].x" 1.4285714626312256;
	setAttr ".tgi[0].ni[9].y" -420;
	setAttr ".tgi[0].ni[9].nvs" 18304;
	setAttr ".tgi[0].ni[10].x" 1604.2857666015625;
	setAttr ".tgi[0].ni[10].y" -467.14285278320312;
	setAttr ".tgi[0].ni[10].nvs" 18304;
	setAttr ".tgi[0].ni[11].x" 1325.7142333984375;
	setAttr ".tgi[0].ni[11].y" -1.4285714626312256;
	setAttr ".tgi[0].ni[11].nvs" 18304;
	setAttr ".tgi[0].ni[12].x" 785.71429443359375;
	setAttr ".tgi[0].ni[12].y" -455.71429443359375;
	setAttr ".tgi[0].ni[12].nvs" 18304;
	setAttr ".tgi[0].ni[13].x" 524.28570556640625;
	setAttr ".tgi[0].ni[13].y" -502.85714721679687;
	setAttr ".tgi[0].ni[13].nvs" 18304;
	setAttr ".tgi[0].ni[14].x" 1325.7142333984375;
	setAttr ".tgi[0].ni[14].y" -131.42857360839844;
	setAttr ".tgi[0].ni[14].nvs" 18304;
	setAttr ".tgi[0].ni[15].x" 1.4285714626312256;
	setAttr ".tgi[0].ni[15].y" -550;
	setAttr ".tgi[0].ni[15].nvs" 18304;
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
connectAttr "skinCluster1GroupId.id" "skinning_PLYShape.iog.og[0].gid";
connectAttr "skinCluster1Set.mwc" "skinning_PLYShape.iog.og[0].gco";
connectAttr "groupId2.id" "skinning_PLYShape.iog.og[1].gid";
connectAttr "tweakSet1.mwc" "skinning_PLYShape.iog.og[1].gco";
connectAttr "skinCluster1.og[0]" "skinning_PLYShape.i";
connectAttr "tweak1.vl[0].vt[0]" "skinning_PLYShape.twl";
connectAttr "skinning_PLYShape.o" "bruce_Shape0.i";
connectAttr "makeNurbCircle1.oc" "ball_CTLShape.cr";
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
connectAttr "ball_CTL.t" "joint1_parentConstraint1.tg[0].tt";
connectAttr "ball_CTL.rp" "joint1_parentConstraint1.tg[0].trp";
connectAttr "ball_CTL.rpt" "joint1_parentConstraint1.tg[0].trt";
connectAttr "ball_CTL.r" "joint1_parentConstraint1.tg[0].tr";
connectAttr "ball_CTL.ro" "joint1_parentConstraint1.tg[0].tro";
connectAttr "ball_CTL.s" "joint1_parentConstraint1.tg[0].ts";
connectAttr "ball_CTL.pm" "joint1_parentConstraint1.tg[0].tpm";
connectAttr "joint1_parentConstraint1.w0" "joint1_parentConstraint1.tg[0].tw";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "Bruce01_:modelDefault.msg" "Bruce01_RN.asn[0]";
connectAttr "Bruce01_:ROOT.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_:MESH.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_:BRUCE.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_:bruce_0.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_:bruce_Shape0.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_:modelDefault.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "skinning_PLY.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "skinning_PLYShape.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "bruce_0.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "bruce_Shape0.iog" "Bruce01_:modelDefault_CON.dsm" -na;
connectAttr "Bruce01_RN.msg" "Bruce01_:modelDefault_CON.dnsm" -na;
connectAttr "ball_CTL.iog" "controls_SET.dsm" -na;
connectAttr "skinCluster1GroupParts.og" "skinCluster1.ip[0].ig";
connectAttr "skinCluster1GroupId.id" "skinCluster1.ip[0].gi";
connectAttr "bindPose1.msg" "skinCluster1.bp";
connectAttr "joint1.wm" "skinCluster1.ma[0]";
connectAttr "joint1.liw" "skinCluster1.lw[0]";
connectAttr "joint1.obcc" "skinCluster1.ifcl[0]";
connectAttr "groupParts2.og" "tweak1.ip[0].ig";
connectAttr "groupId2.id" "tweak1.ip[0].gi";
connectAttr "skinCluster1GroupId.msg" "skinCluster1Set.gn" -na;
connectAttr "skinning_PLYShape.iog.og[0]" "skinCluster1Set.dsm" -na;
connectAttr "skinCluster1.msg" "skinCluster1Set.ub[0]";
connectAttr "tweak1.og[0]" "skinCluster1GroupParts.ig";
connectAttr "skinCluster1GroupId.id" "skinCluster1GroupParts.gi";
connectAttr "groupId2.msg" "tweakSet1.gn" -na;
connectAttr "skinning_PLYShape.iog.og[1]" "tweakSet1.dsm" -na;
connectAttr "tweak1.msg" "tweakSet1.ub[0]";
connectAttr "skinning_PLYShapeOrig.w" "groupParts2.ig";
connectAttr "groupId2.id" "groupParts2.gi";
connectAttr "ROOT.msg" "bindPose1.m[0]";
connectAttr "DATA.msg" "bindPose1.m[1]";
connectAttr "joint1.msg" "bindPose1.m[2]";
connectAttr "bindPose1.w" "bindPose1.p[0]";
connectAttr "bindPose1.m[0]" "bindPose1.p[1]";
connectAttr "bindPose1.m[1]" "bindPose1.p[2]";
connectAttr "joint1.bps" "bindPose1.wm[2]";
connectAttr "bruce_0.iog" "out_SET.dsm" -na;
connectAttr "ROOT.iog" "rigDefault_SET.dsm" -na;
connectAttr "controls_SET.msg" "rigDefault_SET.dnsm" -na;
connectAttr "out_SET.msg" "rigDefault_SET.dnsm" -na;
connectAttr "skinning_PLYShape.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[0].dn"
		;
connectAttr "skinCluster1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[1].dn";
connectAttr "bruce_Shape0.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[2].dn";
connectAttr "groupParts2.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[3].dn";
connectAttr ":initialShadingGroup.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[4].dn"
		;
connectAttr "skinCluster1GroupId.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[5].dn"
		;
connectAttr "Bruce01_:modelDefault_CON.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[6].dn"
		;
connectAttr "skinCluster1Set.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[7].dn";
connectAttr "skinCluster1GroupParts.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[8].dn"
		;
connectAttr "skinning_PLYShapeOrig.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[9].dn"
		;
connectAttr "tweakSet1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[10].dn";
connectAttr "skinning_PLY.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[11].dn";
connectAttr "joint1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[12].dn";
connectAttr "tweak1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[13].dn";
connectAttr "bruce_0.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[14].dn";
connectAttr "groupId2.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[15].dn";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "skinning_PLYShape.iog" ":initialShadingGroup.dsm" -na;
connectAttr "bruce_Shape0.iog" ":initialShadingGroup.dsm" -na;
connectAttr "Bruce01_:bruce_Shape0.iog" ":initialShadingGroup.dsm" -na;
// End of source.ma
