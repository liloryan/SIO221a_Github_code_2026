function [f, P] = windSpectrum(data, dt, doDetrend, doDemean, useHann)
    
% WINDSPECTRUM Compute the PSD of a signal.
%   [f, P] = windSpectrum(data, dt) uses the input samples as supplied.
%   [f, P] = windSpectrum(data, dt, doDetrend, doDemean, useHann)
%   optionally removes a linear trend, removes the mean, or applies a
%   periodic Hann (Hanning) window. All three options default to false.
%
%
%   data is a finite row or column vector.
%   dt is the sample interval in seconds.
%   f is the frequency vector in Hz, including zero.
%   P is the one-sided power spectral density in input units squared per Hz.
% 
% 
% Ely J. Dawson
% Nov 8, 2026
% SIOC - 221A

    % Set defaults for omitted preprocessing options.
    if nargin < 3
        doDetrend = false;
    end
    if nargin < 4
        doDemean = false;
    end
    if nargin < 5
        useHann = false;
    end

    % The FFT requires finite samples and a positive sample interval.
    validateattributes(data, {'numeric'}, {'vector', 'real', 'finite'});
    validateattributes(dt, {'numeric'}, ...
        {'scalar', 'real', 'finite', 'positive'});

    x = double(data(:));
    N = numel(x);
    if N < 2
        error('The input must contain at least two samples.');
    end

    % A linear detrend removes the fitted slope and intercept.
    % Demeaning alone removes only the sample mean.
    if doDetrend
        x = detrend(x, 1);
    elseif doDemean
        x = x - mean(x);
    end

    % Use unit weights by default, or taper with a periodic Hann window.
    w = ones(N, 1);
    if useHann
        n = (0:N-1)';
        w = 0.5 - 0.5*cos(2*pi*n/N);
    end

    % Convert the sample interval to a sampling frequency and build the
    % nonnegative frequency grid, including Nyquist when N is even.
    Fs = 1 / dt;
    nFreq = floor(N/2) + 1;
    f = (0:nFreq-1)' * Fs / N;

    % Normalize by sampling frequency and window energy to obtain a PSD.
    X = fft(x .* w);
    P = abs(X(1:nFreq)).^2 / (Fs * sum(w.^2));

    % Fold negative-frequency power into the matching positive bins.
    lastBin = nFreq - (mod(N, 2) == 0);
    P(2:lastBin) = 2 * P(2:lastBin);
end