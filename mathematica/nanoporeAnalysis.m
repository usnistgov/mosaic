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


genKeyList[]:={{"stepheight",1},{"opencurr",2},{"eventstart",3},{"eventend",4},{"tau",5},{"abseventstart",6},{"blockdepth",7},{"status",8},{"chisq",9}}


MDKey[key_]:=Module[{tab},
(tab[#[[1]]]=#[[2]])&/@genKeyList[];
Return[tab[key]]
]


PrintMDKeys[]:=Module[{tab},
(tab[#[[1]]]=#[[2]])&/@genKeyList[];
DownValues[tab][[All,1,1,1]]
]


(* ::Text:: *)
(*ProcessingStatus	OpenChCurrent (pA)	BlockedCurrent (pA)	EventStart (ms)	EventEnd (ms)	BlockDepth (ms)	ResTime (ms)	RCConstant (ms)	AbsEventStart (ms)	ReducedChiSquared*)


MDTransform={#[[2]]-#[[3]],#[[2]],#[[4]],#[[5]],#[[8]],#[[9]],#[[6]],#[[1]],#[[10]]}&;


frTicks[rng_]:=rng/;rng==Automatic
frTicks[rng_]:={#,#,{0.02,0}}&/@rng


PlotEvent[dat_,fit_,\[Delta]t_,nPts_,plotmark_:None,skip_:1,yrng_:Range[0,150,25],xrng_:Range[0,2,0.1],pltrng_:Automatic]:=ListPlot[Transpose[{Range[0,Length[dat]-1]\[Delta]t,Abs[dat]}][[;;;;skip]],PlotRange->All,PlotStyle->Red]/;fit[[MDKey["status"]]]!="normal"
PlotEvent[dat_,fit_,\[Delta]t_,nPts_,plotmark_:None,skip_:1,yrng_:Range[0,150,25],xrng_:Range[0,2,0.1],pltrng_:Automatic]:=Block[{a,t,b,\[Mu]1,\[Mu]2,\[Tau],prng=pltrng},
prng=prng/.e_/;prng==Automatic->{fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]]-15,fit[[MDKey["opencurr"]]]+15};
Show[{
ListPlot[Transpose[{Range[0,Length[dat]-1]\[Delta]t,Abs[dat]}][[Max[1,IntegerPart[fit[[MDKey["eventstart"]]]/\[Delta]t]-nPts];;Min[IntegerPart[fit[[MDKey["eventend"]]]/\[Delta]t]+nPts,Length[dat]];;skip]],PlotRange->prng,PlotStyle->Directive[RGBColor@@({41, 74,130}/255),Opacity[0.75]],PlotMarkers->plotmark,Epilog->{Gray,Dashing[{0.01,0.02}],Thickness[0.005],
Line[{{(IntegerPart[fit[[MDKey["eventstart"]]]/\[Delta]t]-nPts)\[Delta]t,fit[[MDKey["opencurr"]]]},{fit[[MDKey["eventstart"]]],fit[[MDKey["opencurr"]]]}}],Line[{{fit[[MDKey["eventend"]]],fit[[MDKey["opencurr"]]]},{100,fit[[MDKey["opencurr"]]]}}],
Line[{{fit[[MDKey["eventstart"]]],fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]]},{fit[[MDKey["eventend"]]],fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]]}}],
Line[{{fit[[MDKey["eventstart"]]],fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]]},{fit[[MDKey["eventstart"]]],fit[[MDKey["opencurr"]]]}}],Line[{{fit[[MDKey["eventend"]]],fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]]},{fit[[MDKey["eventend"]]],fit[[MDKey["opencurr"]]]}}],Black,Thickness[0.005],Dashing[{}],Line[{{(Max[1,IntegerPart[fit[[MDKey["eventstart"]]]/\[Delta]t]-nPts]+3) \[Delta]t,(fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]])+0},{(Max[1,IntegerPart[fit[[MDKey["eventstart"]]]/\[Delta]t]-nPts]+3) \[Delta]t,(fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]])+10}}],Line[{{(Max[1,IntegerPart[fit[[MDKey["eventstart"]]]/\[Delta]t]-nPts]+3) \[Delta]t,(fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]])},{(Max[1,IntegerPart[fit[[MDKey["eventstart"]]]/\[Delta]t]-nPts]+8) \[Delta]t,(fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]])}}],Text[Style["5 \[Mu]s",24,FontFamily->"Helvetica"],{(Max[1,IntegerPart[fit[[MDKey["eventstart"]]]/\[Delta]t]-nPts]+5.5) \[Delta]t,(fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]])-5}],Text[Rotate[Style["10 pA",24,FontFamily->"Helvetica"],\[Pi]/2],{(Max[1,IntegerPart[fit[[MDKey["eventstart"]]]/\[Delta]t]-nPts]+1.5) \[Delta]t,(fit[[MDKey["opencurr"]]]-fit[[MDKey["stepheight"]]])+5}]},Frame->True,FrameStyle->Thick,FrameTicks->{{frTicks[yrng],None},{frTicks[xrng],None}},FrameTicksStyle->Directive[40,FontFamily->"Helvetica"],FrameLabel->{Style["\!\(\*
StyleBox[\"t\",\nFontSlant->\"Italic\"]\) (ms)",40,FontFamily->"Helvetica"],Style["|\!\(\*
StyleBox[\"i\",\nFontSlant->\"Italic\"]\)\!\(\*
StyleBox[\"|\",\nFontSlant->\"Italic\"]\) (pA)",40,FontFamily->"Helvetica"]},ImageSize->800],
ListLinePlot[{
Table[{t,((a( (-1+E^((-t+\[Mu]1)/\[Tau])) HeavisideTheta[t-\[Mu]1]+(1-E^((-t+\[Mu]2)/\[Tau])) HeavisideTheta[t-\[Mu]2])+b)/.{\[Tau]->fit[[MDKey["tau"]]],\[Mu]1->fit[[MDKey["eventstart"]]],\[Mu]2->fit[[MDKey["eventend"]]],a->fit[[MDKey["stepheight"]]],b->fit[[MDKey["opencurr"]]]})},{t,(IntegerPart[fit[[MDKey["eventstart"]]]/\[Delta]t]-nPts)\[Delta]t,(IntegerPart[fit[[MDKey["eventend"]]]/\[Delta]t]+nPts)\[Delta]t,\[Delta]t/10}]
},PlotRange->All,PlotStyle->{{Black,Thickness[0.006]}}]}]
]


PlotBlockDepth[datpath_,filt_,bin_,pltstyle_:Automatic]:=Module[{md =MDTransform/@Flatten[Import[#,"TSV"][[2;;]]&/@FileNames["eventMD*tsv",datpath],1],d1},
d1=Select[md,filt];
Return[ListLinePlot[PDF1D[d1[[All,7]],bin[[;;2]],bin[[3]]],PlotRange->All,PlotStyle->pltstyle]]
]


MeanBDGauss[datpath_,filt_]:=Module[{md =MDTransform/@Flatten[Import[#,"TSV"][[2;;]]&/@FileNames["eventMD*tsv",datpath],1],d1},
d1=Select[md,filt];
Return[{Mean[d1[[All,7]]],StandardDeviation[d1[[All,7]]],StandardError[d1[[All,7]]]}]
]


MeanResTimeExp[datpath_,filt_,bin_,resest_]:=Module[{md =MDTransform/@Flatten[Import[#,"TSV"][[2;;]]&/@FileNames["eventMD*tsv",datpath],1],d1,hist,ft,a,b,t},
d1=Select[md,filt];
hist=Hist1D[d1[[All,4]]-d1[[All,3]],bin[[;;2]],bin[[3]]];
ft=NonlinearModelFit[hist,a Exp[-b t],{{a,hist[[1]][[2]]},{b,1/resest}},t];
Return[{1/b/.ft["BestFitParameters"],
Show[{
ListLogPlot[hist,PlotRange->All,PlotMarkers->Automatic],
LogPlot[Evaluate[Normal[ft]],{t,bin[[1]],bin[[2]]}]}]
}]
]


PlotAnalysis[folder_, bin_List,bint_List, filt_]:=Module[{md =MDTransform/@Flatten[Import[#,"TSV"][[2;;]]&/@FileNames["eventMD*tsv",folder],1],d1},
d1=Select[md,filt];
GraphicsRow[{
ListLinePlot[Hist1D[d1[[All,7]],bin[[;;2]],bin[[3]]],PlotRange->All,Epilog->{Text[Style["nEvents="<>ToString[Length[d1]],16],Scaled[{0.2,0.7}]]}],
ListLogPlot[Hist1D[d1[[All,5]],bint[[;;2]],bint[[3]]],PlotRange->All,Joined->True,PlotMarkers->{Automatic,14}]
}]
]


PlotEvents[folder_,FsKHz_]:=Module[{
md =MDTransform/@Flatten[Import[#,"TSV"][[2;;]]&/@FileNames["eventMD.tsv",folder],1],
ts=Import[folder<>"/eventTS.csv","CSV"]
},
Manipulate[PlotEvent[ts[[i]],md[[i]],1/FsKHz,20,{Automatic,16},s,Automatic,Automatic],{i,1,Length[md],1,Appearance->"Open"},{s,1,10,1,Appearance->"Open"}]
]


CaptureRate[art_,cutoff_]:=Module[{h1=Hist1D[art,{0,cutoff},cutoff/1000],a,\[Lambda],t,ft},ft=NonlinearModelFit[Transpose[{h1[[All,1]],h1[[All,2]]/h1[[All,2]][[1]]}],a Exp[-(t/\[Lambda])],{{a,1},{\[Lambda],Mean[art]}},t];
Return[{1/\[Lambda],1/(\[Lambda] Sqrt[Length[art]])}/.ft["BestFitParameters"]]
]


(* ::Text:: *)
(*CaptureRate[art_,blksz_]:=#[1/Mean/@Partition[art,blksz]]&/@{Mean,StandardError}*)


ArrivalTimes[md_]:=Flatten[Differences/@Partition[md[[All,MDKey["abseventstart"]]],2,1]]/1000


kon[cap_,c_]:=1/((1/cap)c)


(* ::Input:: *)
(*PlotEvent2[ts_,md_,Fs_]:=Module[{},*)
(*Show[{*)
(*ListLinePlot[Table[{t,First[Differences[md[[{3,2}]]]]((1-Exp[-((t-md[[5]])/md[[8]])])HeavisideTheta[t-md[[5]]]-(1-Exp[-((t-md[[4]])/md[[8]])])HeavisideTheta[t-md[[4]]])+md[[2]]},{t,0,Length[ts] 1/Fs,1/(5 Fs)}],PlotRange->All,PlotStyle->{Black,Thickness[0.006]}],*)
(*ListPlot[Transpose[{Range[0,Length[ts]-1] 1/Fs,Abs[ts]}],PlotRange->All,PlotStyle->Directive[RGBColor@@({41, 74,130}/255),Opacity[0.75]],PlotMarkers->{Automatic,14}]*)
(*},Frame->True,FrameStyle->Thick,FrameTicks->{{Automatic,None},{Automatic,None}},FrameTicksStyle->Directive[30,FontFamily->"Helvetica"],FrameLabel->{Style["\!\(\**)
(*StyleBox[\"t\",\nFontSlant->\"Italic\"]\) (ms)",30,FontFamily->"Helvetica"],Style["|\!\(\**)
(*StyleBox[\"i\",\nFontSlant->\"Italic\"]\)\!\(\**)
(*StyleBox[\"|\",\nFontSlant->\"Italic\"]\) (pA)",30,FontFamily->"Helvetica"]},ImageSize->800]*)
(*]/;md[[1]]=="normal"*)
(*PlotEvent2[ts_,md_,Fs_]:=ListPlot[Transpose[{Range[0,Length[ts]-1] 1/Fs,Abs[ts]}],PlotRange->All,PlotStyle->Red,Frame->True,FrameStyle->Thick,FrameTicks->{{Automatic,None},{Automatic,None}},FrameTicksStyle->Directive[30,FontFamily->"Helvetica"],FrameLabel->{Style["\!\(\**)
(*StyleBox[\"t\",\nFontSlant->\"Italic\"]\) (ms)",30,FontFamily->"Helvetica"],Style["|\!\(\**)
(*StyleBox[\"i\",\nFontSlant->\"Italic\"]\)\!\(\**)
(*StyleBox[\"|\",\nFontSlant->\"Italic\"]\) (pA)",30,FontFamily->"Helvetica"]},ImageSize->800]*)


PlotEvents2[folder_,FsKHz_]:=Module[{
md =MDTransform/@Flatten[Import[#,"TSV"][[2;;]]&/@FileNames["eventMD.tsv",folder],1],
ts=Import[folder<>"/eventTS.csv","CSV"]
},
Manipulate[PlotEvent[ts[[i]],md[[i]],1/FsKHz,20,{Automatic,16},s,Automatic,Automatic],{i,1,Length[md],1,Appearance->"Open"},{s,1,10,1,Appearance->"Open"}]
]
