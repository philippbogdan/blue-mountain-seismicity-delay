
load("Catalog_Data.mat")

%%
Event_no=(1:length(time_vec_DAS))';
%use sidx to sort events by date
[dns,sidx] = sort(time_vec_DAS);                              % Sort By Date, Return Indices

Loc_x=Loc_all_preproc(1,sidx)';

Loc_y=Loc_all_preproc(2,sidx)';

%Path=Path(sidx);
t0=time_vec_DAS';


T = table(Event_no,Loc_x,Loc_y,t0,Magnitude);

writetable(T,'BM_event_DAS_edgeproc_catalog.txt')