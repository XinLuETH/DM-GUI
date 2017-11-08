% [out, H] = butterworth_lowpass(in,fc,n)
%
% Applies a low pass butterworth filter of order "n" and cutoff frequency
% "fc" to array "in". The filtered output is returned by variable "out" and
% the filter transfer function is returned in "H".

function [out, H] = butterworth_lowpass(in,fc,n)

% Create filter transfer function
if isequal(n,0)
    [xi,yi] = meshgrid(linspace(-0.5,0.5,size(in,2)),linspace(-0.5,0.5,size(in,1)));
    H = sqrt(xi.^2+yi.^2) <= fc;
    H = fftshift(H);
else
    H = lowpassfilter(size(in), fc, n);
end

% Apply filter to input array
in_f = fft2(in);
out_f =in_f .* H;
out = ifft2(out_f,'symmetric');
