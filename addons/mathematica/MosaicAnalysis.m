(* ::Package:: *)

<<Util`


CaptureRate[absstart_,stime_,etime_,nbins_]:=Module[{at=ArrivalTimes[absstart],a,\[Lambda],t,ft,h1},

h1=Hist1D[at,{stime,etime},(etime-stime)/nbins];
ft=NonlinearModelFit[Transpose[{h1[[All,1]],h1[[All,2]]/h1[[All,2]][[1]]}],a Exp[-(t/\[Lambda])],{{a,1},{\[Lambda],Mean[at]}},t];
Return[{{1/\[Lambda],1/(\[Lambda] Sqrt[Length[at]])}/.ft["BestFitParameters"],
Show[{
ListLogPlot[Transpose[{h1[[All,1]],h1[[All,2]]/h1[[All,2]][[1]]}],PlotRange->{{stime,etime},All},PlotMarkers->Automatic, Frame->True, FrameLabel->{"\!\(\*SubscriptBox[\(T\), \(on\)]\) (ms)","Probability (ms\!\(\*SuperscriptBox[\()\), \(-1\)]\)"}, Epilog->{Text[NumberForm[1/\[Lambda],{4,0}]\[PlusMinus]NumberForm[1/(\[Lambda] Sqrt[Length[at]]),{2,1}]/.ft["BestFitParameters"],{(etime-stime)/2,Log[0.5]}]}],
LogPlot[Evaluate[Normal[ft]],{t,stime,etime},PlotStyle->Thick]
},ImageSize->300]
}]
]


ArrivalTimes[arrtime_]:=Flatten[Differences/@Partition[arrtime,2,1]]/1000


kon[cap_,c_]:=1/((1/cap)c)


MeanResTime[tmin_, tmax_,nbins_, filenames_,fileList_,restriction_]:=Module[{q,pdf,ft,a,b,t},
q=Flatten[QueryDB[FileNames["*.sqlite",#][[-1]],"select ResTime from metadata where ProcessingStatus='normal' and "<>ToString[restriction]]]&/@fileList;
pdf=PDF1D[#,{tmin,tmax},nbins]&/@q;
ft=NonlinearModelFit[#,a*Exp[-t/b],{a,b},t,MaxIterations->5000]&/@pdf;
plot1=ListLogPlot[pdf,Frame->True,FrameLabel->{"<\[Tau]> (ms)","Probability Density (1/ms)"}];
plot2=LogPlot[Evaluate[Normal/@ft],{t,10^(-4),tmax},PlotLegends->filenames];
Show[plot1,plot2]]


(* ::Text:: *)
(*Function which returns the number of events fit which fulfill "restriction". When the optional argument AllRuns->"True" is used, all .sqlite files in directory are probed, otherwise the default is falseThis allows user to compare different analysis settings used on the same file.*)


Options[NumberOfEvents]={AllRuns->"False"};
NumberOfEvents[fileList_,restriction_,OptionsPattern[]]:=
MatrixForm[
	Table[{i,Length[SortBy[QueryDB[FileNames["*.sqlite", #][[i]],
		"select ResTime from metadata where ProcessingStatus='normal' and "<>ToString[restriction]], Last][[All,1]]]},
		{i,-1,-1}],
	TableHeadings->{None,{FileNameTake[#]<>"\n Index","\n# Events Fit"}}]&/@fileList/;OptionValue[AllRuns]=="False"

NumberOfEvents[fileList_,restriction_,OptionsPattern[]]:=
MatrixForm[
	Table[{i,Length[SortBy[QueryDB[FileNames["*.sqlite", #][[i]],
		"select ResTime from metadata where ProcessingStatus='normal' and "<>ToString[restriction]], Last][[All,1]]]},
		{i,Evaluate[Length[FileNames["*sqlite",#]]]}],
	TableHeadings->{None,{FileNameTake[#]<>"\n Index","\n# Events Fit"}}]&/@fileList/;OptionValue[AllRuns]=="True"


