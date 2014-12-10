(* ::Package:: *)

(* ::Text:: *)
(*Utility functions for use within Mathematica*)
(**)
(*:created: 	11/1/2014*)
(*:author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>*)
(*:License:	See LICENSE.TXT	*)

StandardError=StandardDeviation[#]/Sqrt[Length[#]]&;


CFormToReal[dat_]:=Block[{a=ToExpression/@StringSplit[dat,{"E","e"}]},Return[a[[1]]*10^a[[2]]]]/;Length[StringSplit[dat,{"E","e"}]]==2
CFormToReal[dat_]:=ToExpression[dat]/;Length[StringSplit[dat,{"E","e"}]]==1


PDF1D[dat_,binspec_List,\[Delta]_]:=Transpose[{Range[binspec[[1]]+\[Delta]/2,binspec[[2]]-\[Delta]/2,\[Delta]],BinCounts[dat,{binspec[[1]],binspec[[2]],\[Delta]}]/(Length[dat] \[Delta])}]


Hist1D[dat_,binspec_List,\[Delta]_]:=Transpose[{Range[binspec[[1]]+\[Delta]/2,binspec[[2]]-\[Delta]/2,\[Delta]],BinCounts[dat,{binspec[[1]],binspec[[2]],\[Delta]}]}]


PDF2D[dat_,binspec_List,\[Delta]_]:=Flatten/@Flatten[Transpose/@Transpose[{Table[{i,j},{i,binspec[[1]]+\[Delta]/2,binspec[[2]]-\[Delta]/2,\[Delta]},{j,binspec[[1]]+\[Delta]/2,binspec[[2]]-\[Delta]/2,\[Delta]}],BinCounts[dat,{binspec[[1]],binspec[[2]],\[Delta]},{binspec[[1]],binspec[[2]],\[Delta]}]/(Length[dat] \[Delta]^2)}],1]


Hist2D[dat_,binspec_List,\[Delta]_]:=Flatten/@Flatten[Transpose/@Transpose[{Table[{i,j},{i,binspec[[1]]+\[Delta]/2,binspec[[2]]-\[Delta]/2,\[Delta]},{j,binspec[[1]]+\[Delta]/2,binspec[[2]]-\[Delta]/2,\[Delta]}],BinCounts[dat,{binspec[[1]],binspec[[2]],\[Delta]},{binspec[[1]],binspec[[2]],\[Delta]}]}],1]


ReadIonPosFile[fname_]:=Flatten[StringSplit[#]][[2;;]]&/@Import[fname,"TSV"]


(* ::Input:: *)
(*PDFMoment[pdf_,n_]:=Total[(#[[1]]^n*#[[2]])&/@pdf]/Total[Last[Transpose[pdf]]]*)
