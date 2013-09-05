(* ::Package:: *)

<<Util`


(* ::Subsubsection:: *)
(*Run Analysis*)


pySetup[]:="
import SingleChannelAnalysis

from eventSegment import *

from singleStepEvent import *
from stepResponseAnalysis import *

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


RunAnalysis[datapath_,filetype_,fileopts_,segment_,analysis_,coderoot_]:=Block[{},
GenPytonScript[datapath,filetype,fileopts,segment,analysis,coderoot];
ReadList["!sh "<>coderoot<>"/mathematica/runAnalysis.sh "<> coderoot <>" &> "<>coderoot<>"/.tmp"];
FilePrint[coderoot<>"/.tmp"]
]


(* ::Subsubsection:: *)
(*Plot Results*)


genKeyList[]:={{"stepheight",1},{"opencurr",2},{"eventstart",3},{"eventend",4},{"tau",5},{"chisq",6},{"blockdepth",7},{"status",8}}


MDKey[key_]:=Module[{tab},
(tab[#[[1]]]=#[[2]])&/@genKeyList[];
Return[tab[key]]
]


PrintMDKeys[]:=Module[{tab},
(tab[#[[1]]]=#[[2]])&/@genKeyList[];
DownValues[tab][[All,1,1,1]]
]


MDTransform={#[[2]]-#[[3]],#[[2]],#[[4]],#[[5]],#[[8]],#[[9]],#[[6]],#[[1]]}&;


frTicks[rng_]:=rng/;rng==Automatic
frTicks[rng_]:={#,#,{0.02,0}}&/@rng


PlotEvent[dat_,fit_,\[Delta]t_,nPts_,plotmark_:None,skip_:1,yrng_:Range[0,150,25],xrng_:Range[0,2,0.1],pltrng_:Automatic]:=ListPlot[Transpose[{Range[0,Length[dat]-1]\[Delta]t,Abs[dat]}][[;;;;skip]],PlotRange->All,PlotStyle->Red]/;fit[[-1]]!="normal"
PlotEvent[dat_,fit_,\[Delta]t_,nPts_,plotmark_:None,skip_:1,yrng_:Range[0,150,25],xrng_:Range[0,2,0.1],pltrng_:Automatic]:=Block[{a,t,b,\[Mu]1,\[Mu]2,\[Tau],prng=pltrng},
prng=prng/.e_/;prng==Automatic->{fit[[2]]-fit[[1]]-15,fit[[2]]+15};
Show[{
ListPlot[Transpose[{Range[0,Length[dat]-1]\[Delta]t,Abs[dat]}][[Max[1,IntegerPart[fit[[3]]/\[Delta]t]-nPts];;Min[IntegerPart[fit[[4]]/\[Delta]t]+nPts,Length[dat]];;skip]],PlotRange->prng,PlotStyle->Directive[RGBColor@@({41, 74,130}/255),Opacity[0.75]],PlotMarkers->plotmark,Epilog->{Gray,Dashing[{0.01,0.02}],Thickness[0.005],
Line[{{(IntegerPart[fit[[3]]/\[Delta]t]-nPts)\[Delta]t,fit[[2]]},{fit[[3]],fit[[2]]}}],Line[{{fit[[4]],fit[[2]]},{100,fit[[2]]}}],
Line[{{fit[[3]],fit[[2]]-fit[[1]]},{fit[[4]],fit[[2]]-fit[[1]]}}],
Line[{{fit[[3]],fit[[2]]-fit[[1]]},{fit[[3]],fit[[2]]}}],Line[{{fit[[4]],fit[[2]]-fit[[1]]},{fit[[4]],fit[[2]]}}],Black,Thickness[0.005],Dashing[{}],Line[{{(Max[1,IntegerPart[fit[[3]]/\[Delta]t]-nPts]+3) \[Delta]t,(fit[[2]]-fit[[1]])+0},{(Max[1,IntegerPart[fit[[3]]/\[Delta]t]-nPts]+3) \[Delta]t,(fit[[2]]-fit[[1]])+10}}],Line[{{(Max[1,IntegerPart[fit[[3]]/\[Delta]t]-nPts]+3) \[Delta]t,(fit[[2]]-fit[[1]])},{(Max[1,IntegerPart[fit[[3]]/\[Delta]t]-nPts]+8) \[Delta]t,(fit[[2]]-fit[[1]])}}],Text[Style["5 \[Mu]s",24,FontFamily->"Helvetica"],{(Max[1,IntegerPart[fit[[3]]/\[Delta]t]-nPts]+5.5) \[Delta]t,(fit[[2]]-fit[[1]])-5}],Text[Rotate[Style["10 pA",24,FontFamily->"Helvetica"],\[Pi]/2],{(Max[1,IntegerPart[fit[[3]]/\[Delta]t]-nPts]+1.5) \[Delta]t,(fit[[2]]-fit[[1]])+5}]},Frame->True,FrameStyle->Thick,FrameTicks->{{frTicks[yrng],None},{frTicks[xrng],None}},FrameTicksStyle->Directive[40,FontFamily->"Helvetica"],FrameLabel->{Style["\!\(\*
StyleBox[\"t\",\nFontSlant->\"Italic\"]\) (ms)",40,FontFamily->"Helvetica"],Style["|\!\(\*
StyleBox[\"i\",\nFontSlant->\"Italic\"]\)\!\(\*
StyleBox[\"|\",\nFontSlant->\"Italic\"]\) (pA)",40,FontFamily->"Helvetica"]},ImageSize->800],
ListLinePlot[{
Table[{t,((a( (-1+E^((-t+\[Mu]1)/\[Tau])) HeavisideTheta[t-\[Mu]1]+(1-E^((-t+\[Mu]2)/\[Tau])) HeavisideTheta[t-\[Mu]2])+b)/.{\[Tau]->fit[[5]],\[Mu]1->fit[[3]],\[Mu]2->fit[[4]],a->fit[[1]],b->fit[[2]]})},{t,(IntegerPart[fit[[3]]/\[Delta]t]-nPts)\[Delta]t,(IntegerPart[fit[[4]]/\[Delta]t]+nPts)\[Delta]t,\[Delta]t/10}]
},PlotRange->All,PlotStyle->{{Black,Thickness[0.006]}}]}]
]


PlotAnalysis[folder_, bin_List,bint_List, filt_]:=Module[{md =MDTransform/@Flatten[Import[#,"TSV"][[2;;]]&/@FileNames["eventMD*tsv",folder],1],d1},
d1=Select[md,filt];
GraphicsRow[{
ListLinePlot[Hist1D[d1[[All,7]],bin[[;;2]],bin[[3]]],PlotRange->All,Epilog->{Text[Style["nEvents="<>ToString[Length[d1]],16],Scaled[{0.2,0.7}]]}],
ListLogLinearPlot[Hist1D[d1[[All,5]],bint[[;;2]],bint[[3]]],PlotRange->All,Joined->True,PlotMarkers->{Automatic,14}]
}]
]


PlotEvents[folder_,FsKHz_]:=Module[{
md =MDTransform/@Flatten[Import[#,"TSV"][[2;;]]&/@FileNames["eventMD.tsv",folder],1],
ts=Import[folder<>"/eventTS.csv","CSV"]
},
Manipulate[PlotEvent[ts[[i]],md[[i]],1/FsKHz,20,{Automatic,16},s,Automatic,Automatic],{i,1,Length[md],1,Appearance->"Open"},{s,1,10,1,Appearance->"Open"}]
]
