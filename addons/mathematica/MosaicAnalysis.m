(* ::Package:: *)

(* ::Text:: *)
(*Analysis functions that build on MosaicUtils*)
(**)
(*:created: 	11/15/2014*)
(*:author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>*)
(*:License:	See LICENSE.TXT	*)


<<Util`


ScaledSingleExponentialFit[hist_, \[Lambda]_,\[Lambda]0_]:=Module[{a,t,ft},
Return[NonlinearModelFit[Transpose[{hist[[All,1]],hist[[All,2]]/First[hist[[All,2]]]}],a Exp[-(t/\[Lambda])],{{a,1},{\[Lambda],\[Lambda]0}},t]]
]


PlotScaledSingleExponentialFit[hist_, ftfunc_, plotopts_]:=Module[{t,xrng={First[hist[[All,1]]],Last[hist[[All,1]]]}},
Return[Show[{
ListLogPlot[Transpose[{hist[[All,1]],hist[[All,2]]/hist[[All,2]][[1]]}],PlotRange->{xrng,All},PlotMarkers->Automatic,plotopts],
LogPlot[Evaluate[ftfunc[t]],Evaluate[Flatten[{t,xrng}]],plotopts]
}]]
]


CaptureRate[absstart_,stime_,etime_,nbins_,plotopts_:{}]:=Module[{at=ArrivalTimes[absstart],a,\[Lambda],t,ft,h1},

h1=Hist1D[at,{stime,etime},(etime-stime)/nbins];
ft=ScaledSingleExponentialFit[h1,\[Lambda],Mean[at]];
Return[{
{1/\[Lambda],1/(\[Lambda] Sqrt[Length[at]])}/.ft["BestFitParameters"],PlotScaledSingleExponentialFit[h1, ft["Function"],plotopts],
h1,
ft["Function"]
}]
]


ArrivalTimes[arrtime_]:=Flatten[Differences/@Partition[arrtime,2,1]]/1000


(* ::Text:: *)
(*kon[cap_, c_] := 1/((1/cap) c)*)
