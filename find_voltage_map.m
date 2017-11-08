% [VOLTAGE_MAP] = find_voltage_map(DESIRED_SHAPE, calib_results, Z_subap_unpow, w_posts_unpow, pitch, use_filter)
% 
% Uses "DESIRED_SHAPE" shape input to determine actuator control voltages
% for DM. "Z_subap_unpow" and "w_posts_unpow" provides absolute DM position
% control. If these variabls have zero entries, the DM is controlled
% differentially. The input variable "pitch" is used for calculating the
% mirror coupling force, and "use_filter" is a boolean input to turn on/off
% a low pass filter representative of the DM transfer function. The
% function returns the  voltage map prediction for the desired DM shape.

function [VOLTAGE_MAP] = find_voltage_map(DESIRED_SHAPE, calib_results, Z_subap_unpow, w_posts_unpow, pitch, use_filter)

% Interpolate DESIRED_SHAPE at same resolution used to calibrate DM 
subap_pixel_width = 35;         
DM_subap_width = length(w_posts_unpow);
interp_N = subap_pixel_width*DM_subap_width;

% Find DESIRED_SHAPE dimensions and upsampe/downsample if necessary
[SHAPE_height, SHAPE_width] = size(DESIRED_SHAPE);
if (SHAPE_width~=interp_N) || (SHAPE_height~=interp_N)
    [xi, yi] = meshgrid(linspace(1,SHAPE_width,interp_N),linspace(1,SHAPE_height,interp_N));
    DESIRED_SHAPE_INTERP = interp2(DESIRED_SHAPE,xi,yi);
    
    % Sign change is needed b/c open loop deflection is positive towards substrate
    DESIRED_SHAPE = -DESIRED_SHAPE_INTERP; 
else
    % Sign change is needed b/c open loop deflection is positive towards substrate
    DESIRED_SHAPE = -DESIRED_SHAPE;
end

% Find desired displacement of posts in shape input
range = subap_pixel_width*(1:DM_subap_width)-(subap_pixel_width-1)/2;
[x_posts, y_posts] = meshgrid(range,range);
w_posts = interp2(DESIRED_SHAPE,x_posts,y_posts) + w_posts_unpow;

% The desired shape should be filtered prior to computing mirror forces at
% the actuator posts. It is performed in the DM calibration process, and is
% necessary for predicing voltages for shapes with spatial frequencies
% exceeding 1/pitch. A low-pass butterworth filter is implemented here.
if use_filter
    tau = (DM_subap_width*pitch)/interp_N; % sampling resolution
    omega_max = max(-pi/tau + 2*pi*(0:interp_N)/(tau*interp_N)); % max spatial frequency
    cutoff_period = 0.8*pitch; % filter cutoff period
    cutoff_freq = 1/cutoff_period; % filter cutoff frequency
    filter_size = cutoff_freq*0.5/omega_max*2*pi; % normalized cutoff freq
    filter_order = 3; % order of butterworth filter, i.e. roll off
    [DESIRED_SHAPE, H] = butterworth_lowpass(DESIRED_SHAPE,filter_size,filter_order);
end

% For absolute DM position control, add the unpowered surface figure to the
% desired shape prior to computing mirror forces
DESIRED_SHAPE = DESIRED_SHAPE + Z_subap_unpow;

% Calculate the mirror forces at the actuator posts; Fm (not used) is the pressure
% (N/m^2) exerted on the DM to achieve the desired shape
[Fm_posts, Fm] = calculate_mirror_forces(DESIRED_SHAPE, DM_subap_width, pitch);

% Predict open loop control voltages using DM calibration data
display_index = [];
VOLTAGE_MAP = calculate_voltages(w_posts, Fm_posts, calib_results, display_index);        

