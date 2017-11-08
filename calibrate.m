function [VOLTAGE_MAP] = calibrate(DESIRED_SHAPE)
%% convert the cell DESIRED_SHAPE to array
% convert cell to a 1D array, also string to double
DESIRED_SHAPE = str2double(DESIRED_SHAPE);
%DESIRED_SHAPE = DESIRED_SHAPE*1e-9;  % convert the unit from nm into meter because in the Python driver showmap DESIRED_SHAPE multiplies 1e9
% reshape the array
DESIRED_SHAPE = reshape(DESIRED_SHAPE, [252,252]);
DESIRED_SHAPE = DESIRED_SHAPE';

%% Load calibration data
[calib_results, unpowered_DM_surface, unpowered_post_positions, ...
                     pitch] = load_calibration_data();
                 
%%perdict voltage map
% VOLTAGE_MAP units are percent of 300V (the max driver output); e.g.
% "50" (%) corresponds to 150V.
use_filter = true;
VOLTAGE_MAP = find_voltage_map(DESIRED_SHAPE, calib_results, ...
    unpowered_DM_surface, unpowered_post_positions, pitch, use_filter);

% Check predicted voltages for values exceeding the DM max voltage;
% Although the driver hardware prevents over voltaging the DM, it is good
% practice to also maintain a software safety limit.
max_voltage = 100* 215/300; %The max DM voltage for this example is 215V
VOLTAGE_MAP = max(VOLTAGE_MAP,0);
VOLTAGE_MAP = min(VOLTAGE_MAP,max_voltage);

% reshape the map to match the UPDATE_multiDM
VOLTAGE_MAP = reshape(VOLTAGE_MAP',numel(VOLTAGE_MAP),1);