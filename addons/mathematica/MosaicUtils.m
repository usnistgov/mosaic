(* ::Package:: *)

<<DatabaseLink`


PrintMDKeys[filename_]:=Module[{db=OpenSQLConnection[JDBC["SQLite",filename]],keys},
keys=SQLExecute[db,"PRAGMA table_info(metadata);"][[All,2]];
CloseSQLConnection[db];
Return[keys]
]


QueryDB[filename_,query_]:=Module[{db=OpenSQLConnection[JDBC["SQLite",filename]],q,res},res=SQLExecute[db,query];
CloseSQLConnection[db];
Return[res]
]


DecodeTimeSeries[ts_]:=ImportString[ImportString[ToString[ts],{"Base64","String"}],"Real64"]


ts[dat_,FsKHz_]:=Transpose[{Range[0,Length[dat]-1]/FsKHz,polarity[dat]*dat}]


Options[PlotEvents]={AnalysisAlgorithm->"StepResponseAnalysis"};
PlotEvents[dbname_,FsKHz_,OptionsPattern[]]:=Module[{q},
q=QueryDB[dbname, "select ProcessingStatus, BlockedCurrent, OpenChCurrent, EventStart, EventEnd, RCConstant, TimeSeries from metadata"];
Manipulate[plotsra[q[[i]][[1]], ts[DecodeTimeSeries[q[[i]][[-1]]],FsKHz],q[[i]][[2;;-2]] ,FsKHz],{i,1,Length[q],1,Appearance->"Open"}]
]/;OptionValue[AnalysisAlgorithm]=="StepResponseAnalysis"
PlotEvents[dbname_,FsKHz_,OptionsPattern[]]:=Module[{q},
q=QueryDB[dbname,"select ProcessingStatus, OpenChCurrent, CurrentStep, EventDelay, RCConstant, TimeSeries from metadata"];
Manipulate[plotmsa[q[[i]][[1]], ts[DecodeTimeSeries[q[[i]][[-1]]],FsKHz], {q[[i]][[2]],DecodeTimeSeries[q[[i]][[3]]],DecodeTimeSeries[q[[i]][[4]]],q[[i]][[5]]},FsKHz],{i,1,Length[q],1,Appearance->"Open"}]
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
