(* ::Package:: *)

(* ::Text:: *)
(*Utilities to import MOSAIC output into Mathematica*)
(**)
(*:created: 	11/15/2014*)
(*:author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>*)
(*:License:	See LICENSE.TXT	*)


<<DatabaseLink`


PrintMDKeys[filename_]:=Module[{db=OpenSQLConnection[JDBC["SQLite",filename]],keys},
keys=SQLExecute[db,"PRAGMA table_info(metadata);"][[All,2]];
CloseSQLConnection[db];
Return[keys]
]


PrintMDTypes[filename_]:=Module[{db=OpenSQLConnection[JDBC["SQLite",filename]],mdtypes},
mdtypes=Flatten[SQLExecute[db,"select * from metadata_t limit 1"]];
CloseSQLConnection[db];
Return[mdtypes]
]


QueryDB[filename_,query_]:=Module[{db=OpenSQLConnection[JDBC["SQLite",filename]],q,res},res=SQLExecute[db,query];
CloseSQLConnection[db];
Return[res]
]
QueryDB[filename_,query_]:=Module[{cols=ColNames[query], db=OpenSQLConnection[JDBC["SQLite",filename]],res,hash},
hash=Association[#[[1]]->#[[2]]&/@Transpose[{SQLExecute[db,"PRAGMA table_info(metadata_t)"][[All,2]],First[SQLExecute[db,"select * from metadata_t limit 1"]]}]];
res=DecodeRecord[#,cols, hash]&/@SQLExecute[db,query];
CloseSQLConnection[db];
Return[res]
]/;StringMatchQ[query,RegularExpression["\\bselect\\b.*\\bmetadata\\b.*"]]


ColNames[qstr_]:=Flatten[StringSplit[StringSplit[First[StringSplit[qstr,{"select","from"}]],","]]]


DecodeRecord[rec_,cols_, colhash_]:=Module[{c=ExpandCols[cols,colhash],ct},
ct=colhash/@c;
Return[(DecodeColumn@@#)&/@Transpose[{rec,ct}]]
]


ExpandCols[cols_,colhash_]:=Keys[colhash]/;cols=={"*"}
ExpandCols[cols_,colhash_]:=cols


DecodeColumn[dat_,dtype_]:=DecodeTimeSeries[dat]/;dtype=="REAL_LIST"
DecodeColumn[dat_,dtype_]:=dat


DecodeTimeSeries[ts_]:=ImportString[ImportString[ToString[ts],{"Base64","String"}],"Real64"]


ts[dat_,FsKHz_]:=Transpose[{Range[0,Length[dat]-1]/FsKHz,polarity[dat]*dat}]


Options[PlotEvents]={AnalysisAlgorithm->"StepResponseAnalysis"};
PlotEvents[dbname_,FsKHz_,OptionsPattern[]]:=Module[{q},
q=QueryDB[dbname, "select ProcessingStatus, BlockedCurrent, OpenChCurrent, EventStart, EventEnd, RCConstant, TimeSeries from metadata"];
Manipulate[plotsra[q[[i]][[1]], ts[q[[i]][[-1]],FsKHz],q[[i]][[2;;-2]] ,FsKHz],{i,1,Length[q],1,Appearance->"Open"}]
]/;OptionValue[AnalysisAlgorithm]=="StepResponseAnalysis"
PlotEvents[dbname_,FsKHz_,OptionsPattern[]]:=Module[{q},
q=QueryDB[dbname,"select ProcessingStatus, OpenChCurrent, CurrentStep, EventDelay, RCConstant, TimeSeries from metadata"];
Manipulate[plotmsa[q[[i]][[1]], ts[q[[i]][[-1]],FsKHz], {q[[i]][[2]],q[[i]][[3]],q[[i]][[4]],q[[i]][[5]]},FsKHz],{i,1,Length[q],1,Appearance->"Open"}]
]/;OptionValue[AnalysisAlgorithm]=="MultiStateAnalysis"


(* ::Input:: *)
(*Prolog->{Thick,Dashed,Darker[Red],*)
(*Line[{{md[[3]],md[[1]]},{md[[4]],md[[1]]}}],*)
(*Line[{{md[[3]],md[[2]]},{md[[3]],md[[1]]}}],*)
(*Line[{{md[[4]],md[[2]]},{md[[4]],md[[1]]}}]*)
(*}*)


polarity[ts_]:=Sign[Mean[ts]]


plotmsa[status_,ts_,md_,FsKHz_]:=Module[{t,a,\[Mu]1,\[Mu]2,\[Tau],b},
Show[{
ListPlot[ts,PlotRange->{-25,All},PlotStyle->Directive[RGBColor@@({41, 74,130}/255),Opacity[0.4]],PlotMarkers->{Automatic,14},Frame->True,FrameLabel->{Style["\!\(\*
StyleBox[\"t\",\nFontSlant->\"Italic\"]\) (ms)",20,FontFamily->"Helvectica"],Style["\!\(\*
StyleBox[\"i\",\nFontSlant->\"Italic\"]\) (pA)",20,FontFamily->"Helvectica"]},FrameTicksStyle->Directive[20,FontFamily->"Helvectica"]],
ListPlot[{
Table[{t,Evaluate[Abs[md[[1]]]+\!\(
\*UnderoverscriptBox[\(\[Sum]\), \(i = 1\), \(Length[md[[2]]]\)]\((\(md[[2]]\)[[i]] HeavisideTheta[t - \(md[[3]]\)[[i]]])\)\)]},{t,ts[[1]][[1]],ts[[-1]][[1]],(1/FsKHz)/10}],
Table[{t,Evaluate[Abs[md[[1]]]+\!\(
\*UnderoverscriptBox[\(\[Sum]\), \(i = 1\), \(Length[md[[2]]]\)]\((\(md[[2]]\)[[i]] \((1 - Exp[
\*FractionBox[\(-\((t - \(md[[3]]\)[[i]])\)\), \(md[[4]]\)]])\) HeavisideTheta[t - \(md[[3]]\)[[i]]])\)\)]},{t,ts[[1]][[1]],ts[[-1]][[1]],(1/FsKHz)/10}]
},PlotStyle->{{ColorData["DarkRainbow"][0.95],Dashed,Thickness[0.005]},{Black,Dashing[{}],Thickness[0.005]},{Black,Thickness[0.005]}},Joined->True]
},ImageSize->600]
]/;status=="normal"
 plotmsa[status_,ts_,md_,FsKHz_]:=Module[{t,a,\[Mu]1,\[Mu]2,\[Tau],b},
Show[{
ListPlot[ts,PlotRange->All,PlotStyle->Red,PlotMarkers->{Automatic,10},Frame->True,FrameLabel->{Style["\!\(\*
StyleBox[\"t\",\nFontSlant->\"Italic\"]\) (ms)",20,FontFamily->"Helvectica"],Style["\!\(\*
StyleBox[\"i\",\nFontSlant->\"Italic\"]\) (pA)",20,FontFamily->"Helvectica"]},FrameTicksStyle->Directive[20,FontFamily->"Helvectica"]]
},ImageSize->600]
]


plotsra[status_,ts_,md_,FsKHz_]:=Module[{t,a,\[Mu]1,\[Mu]2,\[Tau],b},
Show[{
ListPlot[ts,PlotRange->{0,All},PlotStyle->Directive[RGBColor@@({41, 74,130}/255),Opacity[0.75]],PlotMarkers->{Automatic,14},Frame->True,FrameLabel->{Style["\!\(\*
StyleBox[\"t\",\nFontSlant->\"Italic\"]\) (ms)",20,FontFamily->"Helvectica"],Style["\!\(\*
StyleBox[\"i\",\nFontSlant->\"Italic\"]\) (pA)",20,FontFamily->"Helvectica"]},FrameTicksStyle->Directive[20,FontFamily->"Helvectica"],Prolog->{Thick,Dashed,Darker[Red],
Line[{{md[[3]],Abs[md[[1]]]},{md[[4]],Abs[md[[1]]]}}],
Line[{{md[[3]],Abs[md[[2]]]},{md[[3]],Abs[md[[1]]]}}],
Line[{{md[[4]],Abs[md[[2]]]},{md[[4]],Abs[md[[1]]]}}]
}],
ListPlot[{
Table[{t,Evaluate[(a( (-1+E^((-t+\[Mu]1)/\[Tau])) HeavisideTheta[t-\[Mu]1]+(1-E^((-t+\[Mu]2)/\[Tau])) HeavisideTheta[t-\[Mu]2])+b)/.{a->Abs[md[[1]]-md[[2]]],b->md[[2]],\[Tau]->md[[5]],\[Mu]1->md[[3]],\[Mu]2->md[[4]]}]},{t,ts[[1]][[1]],ts[[-1]][[1]],(1/FsKHz)/10}]
},PlotStyle->{{Black,Thickness[0.005]},{Black,Thickness[0.005]},{Black,Thickness[0.005]}},Joined->True]
},ImageSize->600]
]/;status=="normal"
 plotsra[status_,ts_,md_,FsKHz_]:=Module[{t,a,\[Mu]1,\[Mu]2,\[Tau],b},
Show[{
ListPlot[ts,PlotRange->All,PlotStyle->Red,PlotMarkers->{Automatic,10},Frame->True,FrameLabel->{Style["\!\(\*
StyleBox[\"t\",\nFontSlant->\"Italic\"]\) (ms)",20,FontFamily->"Helvectica"],Style["\!\(\*
StyleBox[\"i\",\nFontSlant->\"Italic\"]\) (pA)",20,FontFamily->"Helvectica"]},FrameTicksStyle->Directive[20,FontFamily->"Helvectica"]]
},ImageSize->600]
]
