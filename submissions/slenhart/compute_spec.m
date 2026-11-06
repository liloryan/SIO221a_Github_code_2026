function [spectrum, f] = compute_spec(data, dt_min, M, do_detrend, do_hanning)
%compute the average spectrum for the inputed data 
%inputs: 
    %data- data that HAS NOT been segmented! spectrum will be computed for
    %this 
    %dt_min- time between samples in minutes, should be a single value
    %M= the number of desired segments
%optional inputs: 
    %do_detrend true/false- removes trend from the inputed data, which also
    %removes the mean 
    %do_hanning true/false- removes trend from the data and applies hanning
    %window to each segment
%outputs: 
    %spectrum- the average spectrum for all the segments, units of
    %(units of the input data)^2/cpd
    %f - list of all the frequencies in cpd 

% defaults for optional inputs
if nargin < 4
    do_detrend = false;
end
if nargin < 5
    do_hanning = false;
end

% segment the data M segments with 50% overlap
data = data(:);% make sure data is a column
N = length(data);
L = 2*floor(N/(M+1));% points per segment
step = L/2;%50 overlap

segs = zeros(L, M);
for k = 1:M
    istart = (k-1)*step + 1;
    iend = istart + L - 1;
    segs(:, k) = data(istart:iend);
end

% frequencies
dt = dt_min/1440;% time between samples in days
T = dt*L;% segment length in days
df = 1/T;
f = (0:L/2)/T;% frequency list

% optional detrending
if do_detrend
    segs = detrend(segs);
end

% optional Hanning window
if do_hanning
    segs = detrend(segs);
    w = hann(L);
    scale = sqrt(8/3);
    segs = segs.*w*scale;
end

% fft
a = fft(segs);
amp = abs(a(1:L/2+1, :)).^2;
% normalize
amp = amp/L^2;
amp(2:end-1, :) = amp(2:end-1, :)*2;
amp = amp/df;
spectrum = mean(amp, 2);

end

