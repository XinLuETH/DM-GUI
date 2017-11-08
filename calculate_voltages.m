% [voltage_map] = calculate_voltages(w_posts, Fm_posts, calib_data, examine_index)
%
% Uses polynomial fit coefficients in the calibration data array
% "calib_data" to calculate actuator voltage "voltage_map" as a function of
% post deflection "w_posts" and mirror coupling force "Fm_posts". If
% "examine_index" is an acuator number, the calibration surface for that
% actuator is displayed.

function [voltage_map] = calculate_voltages(w_posts, Fm_posts, calib_data, examine_index)
    
% Variable definition
num_subaps = length(w_posts);
num_points = numel(w_posts);

% Check to see if "examine_index" is empty, if not plot data, 
% surface fit and voltage map prediction for the actuator number
% specified
if ~isempty(examine_index)
    coeffs = calib_data{examine_index}.coeff;
    orders = calib_data{examine_index}.orders;
    x = 1e6*reshape(w_posts,num_points,1); % post deflection in um
    y = 1e3*reshape(Fm_posts,num_points,1); % coupling forces in mN

    % The function polyval_xy produces V^2 as a function of post
    % deflection and coupling force using calibration polynomial 
    % coefficients and corresponding orders. 
    voltage_map = polyval_xy(x,y,coeffs,orders);

    % The polynomial fit is performed on V^2 during the calibration
    % process. To determine the voltage map, take the square root.
    voltage_map = sqrt(voltage_map.*(voltage_map>=0));
    voltage_map = reshape(voltage_map,num_subaps,num_subaps);
else
    x = 1e6*reshape(w_posts',num_points,1); % post deflection in um
    y = 1e3*reshape(Fm_posts',num_points,1); % coupling forces in mN
    voltage_map = zeros(num_points,1);

    for ii = 1:num_points
        coeffs = calib_data{ii}.coeff;
        orders = calib_data{ii}.orders;

        % The function polyval_xy produces V^2 as a function of post
        % deflection and coupling force using calibration polynomial 
        % coefficients and corresponding orders. Looping through the
        % acutators to compute voltages is not the most effiecient
        % method to perform these calculations. This can be converted
        % to a matrix computation.
        voltage_map(ii) = polyval_xy(x(ii),y(ii),coeffs,orders);
    end

    % The polynomial fit is performed on V^2 during the calibration
    % process. To determine the voltage map, take the square root.
    voltage_map = sqrt(voltage_map.*(voltage_map>=0));
    voltage_map = reshape(voltage_map,num_subaps,num_subaps)';
end

