(* ::Package:: *)

<<Util`


(* ::Subsubsection:: *)
(*Run Analysis*)


pySetup[]:="
import SingleChannelAnalysis

from eventSegment import *

from singleStepEvent import *
from stepResponseAnalysis import *
from multiStateAnalysis import *

from qdfTrajIO import *
from abfTrajIO import *
from tsvTrajIO import *
from binTrajIO import *

from besselLowpassFilter import *
from convolutionFilter import *\n\n"


pyAnalysisCommand[datpath_,filetype_,fileopts_,segment_,analysis_]:="SingleChannelAnalysis.SingleChannelAnalysis(
\t\t\t"<>filetype<>"(dirname='"<>datpath<>"',"<>fileopts<>"),
\t\t\t"<>segment<>",
\t\t\t"<>analysis<>"
\t\t).Run()"


GenPytonScript[datapath_,filetype_,fileopts_,segment_,analysis_,coderoot_]:=Export[coderoot<>"/analysisScript.py",pySetup[]<>pyAnalysisCommand[datapath,filetype,fileopts,segment,analysis],"Text"]


WriteSettings[settingspath_,ethresh_,writets_,meancurr_:-1,sdcurr_:-1,slopecurr_:-1,mineventlen_:5]:=Export[settingspath<>"/.settings","{
\t\"eventSegment\" : {
\t\t\"blockSizeSec\" \t\t: \"0.5\",
\t\t\"eventPad\" \t\t: \"50\",
\t\t\"minEventLength\" \t: \""<>ToString[mineventlen]<>"\",
\t\t\"eventThreshold\" \t: \""<>ToString[ethresh]<>"\",
\t\t\"driftThreshold\" \t: \"9999.0\",
\t\t\"maxDriftRate\" \t\t: \"100000.0\",
\t\t\"meanOpenCurr\"\t\t: \""<>ToString[meancurr]<>"\",
\t\t\"sdOpenCurr\"\t\t: \""<>ToString[sdcurr]<>"\",
\t\t\"slopeOpenCurr\"\t\t: \""<>ToString[slopecurr]<>"\",
\t\t\"writeEventTS\"\t\t: \""<>ToString[writets]<>"\",
\t\t\"parallelProc\"\t\t: \"0\",
\t\t\"reserveNCPU\"\t\t: \"5\",
\t\t\"plotResults\"\t\t: \"0\"
\t},
\t\"singleStepEvent\" : {
\t\t\"binSize\" \t\t: \"1.0\",
\t\t\"histPad\" \t\t: \"10\",
\t\t\"maxFitIters\"\t\t: \"5000\",
\t\t\"a12Ratio\" \t\t: \"1.e4\",
\t\t\"minEvntTime\" \t\t: \"10.e-6\",
\t\t\"minDataPad\" \t\t: \"75\"
\t},
\t\"stepResponseAnalysis\" : {
\t\t\"FitTol\"\t\t: \"1.e-7\",
\t\t\"FitIters\"\t\t: \"10000\",
\t\t\"BlockRejectRatio\"\t: \"0.9\"
\t},
\t\"multiStateAnalysis\" : {
\t\t\"FitTol\"\t\t: \"1.e-7\",
\t\t\"FitIters\"\t\t: \"10000\",
\t\t\"InitThreshold\"\t: \""<>ToString[ethresh]<>"\"
\t},
\t\"besselLowpassFilter\" : {
\t\t\"filterOrder\"\t\t: \"6\",
\t\t\"filterCutoff\"\t\t: \"10000\",
\t\t\"decimate\"\t\t: \"1\"\t
\t}
}","Text"]


RunAnalysis[datapath_,filetype_,fileopts_,segment_,analysis_,coderoot_]:=Block[{},
GenPytonScript[datapath,filetype,fileopts,segment,analysis,coderoot];
ReadList["!sh "<>coderoot<>"/mathematica/runAnalysis.sh "<> coderoot <>" &> "<>coderoot<>"/.tmp"];
FilePrint[coderoot<>"/.tmp"]
]


(* ::Subsubsection:: *)
(*Plot Results*)


PrintMDKeys[filename_]:=Module[{db=Database`OpenDatabase[filename],keys},
keys=Database`QueryDatabase[db,"PRAGMA table_info(metadata);"][[All,2]];
Database`CloseDatabase[db];
Return[keys]
]


QueryDB[filename_,cols_, status_, query_]:=Module[{db=Database`OpenDatabase[filename],q,res},
q=querystring[cols, status, query];
res=Database`QueryDatabase[db,q[[1]],q[[2]]];
Database`CloseDatabase[db];
Return[res]
]
querystring[cols_,status_,query_]:={"select "<>ToString[cols]<>" from metadata where ( ProcessingStatus = ? and "<>ToString[query]<> " )",{ToString[status,CharacterEncoding->"UTF-8"]}}/;(status !="*"&&query!="")
querystring[cols_,status_,query_]:={"select "<>ToString[cols]<>" from metadata where ( "<>ToString[query]<> " )",{}}/;(status=="*"&& query !="")
querystring[cols_,status_,query_]:={"select "<>ToString[cols]<>" from metadata",{}}/;(status=="*"&& query =="")
querystring[cols_,status_,query_]:={"select "<>ToString[cols]<>" from metadata where ( ProcessingStatus = ? )",{ToString[status,CharacterEncoding->"UTF-8"]}};


DecodeTimeSeries[ts_]:=ImportString[ImportString[ToString[ts],{"Base64","String"}],"Real64"]


(* ::Input:: *)
(*PrintMDKeys[FileNames["*sqlite","/Users/arvind/Research/Experiments/SBSTagsColumbia/dA6TP30odd/p100mV3/"][[-1]]]*)


ts[dat_,FsKHz_]:=Transpose[{Range[0,Length[dat]-1]/FsKHz,dat}]


Options[PlotEvents]={AnalysisAlgorithm->"StepResponseAnalysis"};
PlotEvents[dbname_,FsKHz_,OptionsPattern[]]:=Module[{q},
q=QueryDB[
			dbname, 
			"ProcessingStatus, BlockedCurrent, OpenChCurrent, EventStart, EventEnd, RCConstant, TimeSeries",
			"*",
			""
		];
Manipulate[plotsra[q[[i]][[1]], ts[DecodeTimeSeries[q[[i]][[-1]]],FsKHz],q[[i]][[2;;-2]] ,FsKHz],{i,1,Length[q],1,Appearance->"Open"}]
]/;OptionValue[AnalysisAlgorithm]=="StepResponseAnalysis"
PlotEvents[dbname_,FsKHz_,OptionsPattern[]]:=Module[{q},
q=QueryDB[
			dbname, 
			"ProcessingStatus, OpenChCurrent, CurrentStep, EventDelay, RCConstant, TimeSeries",
			"*",
			""
		];
Manipulate[plotmsa[q[[i]][[1]], ts[DecodeTimeSeries[q[[i]][[-1]]],FsKHz], {q[[i]][[2]],DecodeTimeSeries[q[[i]][[3]]],DecodeTimeSeries[q[[i]][[4]]],q[[i]][[5]]},FsKHz],{i,1,Length[q],1,Appearance->"Open"}]
]/;OptionValue[AnalysisAlgorithm]=="MultiStateAnalysis"


(* ::Input:: *)
(*Prolog->{Thick,Dashed,Darker[Red],*)
(*Line[{{md[[3]],Abs[md[[1]]]},{md[[4]],Abs[md[[1]]]}}],*)
(*Line[{{md[[3]],Abs[md[[2]]]},{md[[3]],Abs[md[[1]]]}}],*)
(*Line[{{md[[4]],Abs[md[[2]]]},{md[[4]],Abs[md[[1]]]}}]*)
(*}*)


plotmsa[status_,ts_,md_,FsKHz_]:=Module[{t,a,\[Mu]1,\[Mu]2,\[Tau],b},
Show[{
ListPlot[Abs[ts],PlotRange->{-25,All},PlotStyle->Directive[RGBColor@@({41, 74,130}/255),Opacity[0.4]],PlotMarkers->{Automatic,14},Frame->True,FrameLabel->{Style["t (ms)",20,FontFamily->"Helvectica"],Style["|i| (pA)",20,FontFamily->"Helvectica"]},FrameTicksStyle->Directive[20,FontFamily->"Helvectica"]],
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
ListPlot[Abs[ts],PlotRange->All,PlotStyle->Red,PlotMarkers->{Automatic,10},Frame->True,FrameLabel->{Style["t (ms)",20,FontFamily->"Helvectica"],Style["|i| (pA)",20,FontFamily->"Helvectica"]},FrameTicksStyle->Directive[20,FontFamily->"Helvectica"]]
},ImageSize->600]
]


plotsra[status_,ts_,md_,FsKHz_]:=Module[{t,a,\[Mu]1,\[Mu]2,\[Tau],b},
Show[{
ListPlot[Abs[ts],PlotRange->{0,All},PlotStyle->Directive[RGBColor@@({41, 74,130}/255),Opacity[0.75]],PlotMarkers->{Automatic,14},Frame->True,FrameLabel->{Style["t (ms)",20,FontFamily->"Helvectica"],Style["|i| (pA)",20,FontFamily->"Helvectica"]},FrameTicksStyle->Directive[20,FontFamily->"Helvectica"],Prolog->{Thick,Dashed,Darker[Red],
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
ListPlot[Abs[ts],PlotRange->All,PlotStyle->Red,PlotMarkers->{Automatic,10},Frame->True,FrameLabel->{Style["t (ms)",20,FontFamily->"Helvectica"],Style["|i| (pA)",20,FontFamily->"Helvectica"]},FrameTicksStyle->Directive[20,FontFamily->"Helvectica"]]
},ImageSize->600]
]


CaptureRate[absstart_,stime_,etime_,nbins_]:=Module[{at=ArrivalTimes[absstart],a,\[Lambda],t,ft,h1},

h1=Hist1D[at,{stime,etime},(etime-stime)/nbins];
ft=NonlinearModelFit[Transpose[{h1[[All,1]],h1[[All,2]]/h1[[All,2]][[1]]}],a Exp[-(t/\[Lambda])],{{a,1},{\[Lambda],Mean[at]}},t];
Return[{{1/\[Lambda],1/(\[Lambda] Sqrt[Length[at]])}/.ft["BestFitParameters"],
Show[{
ListLogPlot[Transpose[{h1[[All,1]],h1[[All,2]]/h1[[All,2]][[1]]}],PlotRange->{{stime,etime},All},PlotMarkers->Automatic,Epilog->{Text[NumberForm[1/\[Lambda],{4,0}]\[PlusMinus]NumberForm[1/(\[Lambda] Sqrt[Length[at]]),{2,1}]/.ft["BestFitParameters"],{(etime-stime)/2,Log[0.5]}]}],
LogPlot[Evaluate[Normal[ft]],{t,stime,etime},PlotStyle->Thick]
},ImageSize->300]
}]
]


ArrivalTimes[dbname_, query_]:=Module[{q=Flatten[QueryDB[dbname, "AbsEventStart","normal",query]]},
Flatten[Differences/@Partition[q,2,1]]/1000
]


ArrivalTimes[arrtime_]:=Flatten[Differences/@Partition[arrtime,2,1]]/1000


kon[cap_,c_]:=1/((1/cap)c)
