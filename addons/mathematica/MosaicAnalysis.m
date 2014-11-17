(* ::Package:: *)

<<Util`


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


ArrivalTimes[arrtime_]:=Flatten[Differences/@Partition[arrtime,2,1]]/1000


kon[cap_,c_]:=1/((1/cap)c)
