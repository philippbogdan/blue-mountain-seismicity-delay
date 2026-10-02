
figure

load('Diffusion_data.mat')

%plot(ym_1./10)

hold on

plot(Vertical_distance_from_injection,'.')

grid on

plot(yp_Upper_curve,'k.')

plot(yp_uncert_1,'r--')

plot(yp_uncert_2,'r--')

%%%




Event_no=(1:length(t_flex_events));
%use sidx to sort events by date
[dns,sidx] = sort(t_flex_events);                              % Sort By Date, Return Indices



%Path=Path(sidx);
t0=t_flex_events;


Event_no=Event_no';
t0=t0';
Vertical_distance_from_injection=Vertical_distance_from_injection';


T = table(Event_no,t0,Vertical_distance_from_injection);

writetable(T,'Vertical_distance_from_injection_FLEX.txt')





