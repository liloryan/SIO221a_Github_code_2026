function [spectrum, f] = compute_spectrum(data,dt_min, do_detrend, do_hanning)
%compute the average spectrum for the inputed data 
%inputs: 
    %data- the segmented data the spectrum is being calculated for, should be
    %(number of data points in each segment, number of segments)
    %dt_min- time between samples in minutes, should be a single value
%optional inputs: 
    %do_detrend true/false- removes trend from the inputed data, which also
    %removes the mean 
    %do_hanning true/false- removes trend from the data and applies hanning
    %window to each segment
%outputs: 
    %spectrum- the average spectrum for all the segments, units of
    %(units of the input data)^2/cpd
    %f - list of all the frequencies in cpd 

    
    
%optional inputs 

if nargin < 3
    do_detrend = false;
end 

if nargin < 4
    do_hanning = false;
end 


L = size(data, 1); %points per segment
dt= dt_min/1440; %time between the samples in days
T = dt*L; %segment length in days
df = 1/T;
f = (0:L/2)/T; %frequency list 


%detrend 
if do_detrend 
    data = detrend(data);
end
   

%hanning
if do_hanning
    data = detrend(data);
    w = hann(L);
    scale = sqrt(8/3);
    data = data.*w*scale;
end
    
%fft
a = fft(data);
amp = abs(a(1:L/2+1, :)).^2;
%normalize
amp = amp/L^2; %normalize
amp(2:end-1, :) = amp(2:end-1, :)*2;% put back the variance from negative
amp = amp/df;%def of the spectrum
spectrum = mean(amp, 2);
end 


