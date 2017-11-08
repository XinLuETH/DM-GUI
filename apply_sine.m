function [DESIRED_SHAPE, VOLTAGE_MAP] = apply_sine(info)
% info is a cell from a python list
subap_pixel_width = 21;              % Number of pixels across DM subaperture

phase = (info{1} * 1/2*pi);

period = (1/info{2}/subap_pixel_width);
amplitude = (info{3} * 1e-9);      % Sin amplitude, peak to valley is 2*amplitude 
direction = info{4};
Zernike = info{5};

DM_subap_width = 12;                 % Number of DM subapertures in Multi-DM
shape_subap_width = 9;              % Size of Zernike pupil, in subapertures  
                                      % this is 9 actuators across
           
offset = 1.5e-6;                        % represents a piston bias below the DM reference plane

% determine array index that corresponds to Zernike pupil                                      
index = DM_subap_width/shape_subap_width;
num_points = subap_pixel_width*DM_subap_width;
i1 = -index;
i2 = index;
   
[xi,yi] = meshgrid(linspace(i1,i2,num_points),linspace(i1,i2,num_points));
[qi,ri] = cart2pol(xi,yi);
IOI = ri<=1;
 
[Xi,Yi] = meshgrid(linspace(0,0,num_points),linspace(0,0,num_points));

% Fill area beyond sine wave with NaNs
zi = zeros(size(xi))+ NaN;

% apply sin wave within the selected area, X represents the axis is x, R
% represents the wave propagates from right to left
start_point = find(IOI(num_points/2,:),1);
switch direction
    case 'X+'
        Xi(1:end,start_point:end) = repmat(linspace(0,num_points-start_point, num_points-start_point+1), num_points,1);%,num_points-start_point+1
        zi(IOI) = amplitude * sin(2*pi*period*Xi(IOI)+phase);%
    case 'X-'
        Xi(1:end,1:num_points-start_point+1) = repmat(linspace(num_points-start_point, 0, num_points-start_point+1), num_points,1);%,num_points-start_point+1
        zi(IOI) = amplitude * sin(2*pi*period*Xi(IOI)+phase);
    case 'Y+'
        Yi(start_point:end,1:end) = repmat(linspace(0,num_points-start_point, num_points-start_point+1)', 1, num_points);%,num_points-start_point+1
        zi(IOI) = amplitude * sin(2*pi*period*Yi(IOI)+phase);%*subap_pixel_width
    case 'Y-'
        Yi(1:num_points-start_point+1,1:end) = repmat(linspace(num_points-start_point, 0, num_points-start_point+1)', 1, num_points);%,num_points-start_point+1
        zi(IOI) = amplitude * sin(2*pi*period*Yi(IOI)+phase); 
    case 'Both+'
        Xi(1:end,start_point:end) = repmat(linspace(0,num_points-start_point, num_points-start_point+1), num_points,1);
        Yi(start_point:end,1:end) = repmat(linspace(0,num_points-start_point, num_points-start_point+1)', 1, num_points);
        zi(IOI) = amplitude * sin(2*pi*period*(Xi(IOI)+Yi(IOI))+phase);%.* sin(2*pi*period*Yi(IOI)+phase);
    case 'Both-'
        Xi(1:end,1:num_points-start_point+1) = repmat(linspace(num_points-start_point, 0, num_points-start_point+1), num_points,1);
        Yi(1:num_points-start_point+1,1:end) = repmat(linspace(num_points-start_point, 0, num_points-start_point+1)', 1, num_points);
        zi(IOI) = amplitude * sin(2*pi*period*(Xi(IOI)+Yi(IOI))+phase);%.*sin(2*pi*period*Yi(IOI)+phase);
end


if Zernike ~= 'N'
    % Fill area beyond Zernike area with NaNs
    zi_Zernike = zeros(size(xi))+ NaN;
    % n and m for the first 15 Zernike fucntions
    n = [0  1  1  2  2 2  3 3  3 3 4 4  4 4  4];
    m = [0  1 -1  0 -2 2 -1 1 -3 3 0 2 -2 4 -4];
    % "zerfun" in as open-source function available on Mathwork's Central
    k = zernfun(n,m,ri(IOI),qi(IOI));

    sum_zernike = zeros(size(ri(IOI)));

    piston = Zernike(1)*1e-9;
    for i = 2:length(n)
        sum_zernike = sum_zernike + 1e-9 * Zernike(i) * k(:,i);
    end
    zi_Zernike(IOI) = sum_zernike;
    zi(IOI) = zi(IOI) + zi_Zernike(IOI);
else
    piston = 0;
end    

BW_PUPIL = ri <=1;
PUPIL_IND = find(BW_PUPIL==1);

% Offset the midpoint plane for the Zernike shape "zi" to about half of 
% the DM actuator stroke, defining the desired shape inside the pupil 
DESIRED_SHAPE = (zi - (max(zi(PUPIL_IND))+ min(zi(PUPIL_IND)))/2 - offset + piston);

% Create desired DM shape outside pupil; Set desired DM deflection at the 
% facesheet perimeter to 0 (corresponds to the edge of two inactive DM 
% rows/colums). Set the remaining array elements so NaNs for interpolation
% below.
DESIRED_SHAPE = padarray(DESIRED_SHAPE,[2*subap_pixel_width,...
                                2*subap_pixel_width],NaN);
DESIRED_SHAPE(1,:) = 0;
DESIRED_SHAPE(:,1) = 0;
DESIRED_SHAPE(:,end) = 0;
DESIRED_SHAPE(end,:) = 0;

% Interpolate NaNs using a plate metaphor. Function available on Matlab
% Central. Slow, but accurate.
DESIRED_SHAPE = inpaint_nans(DESIRED_SHAPE,1); 

% Extract area corresponding to 12x12 DM subapertures
range = (2*subap_pixel_width+1):subap_pixel_width*(2+DM_subap_width);
DESIRED_SHAPE = DESIRED_SHAPE(range,range); 

% figure
% imagesc(1e9*(DESIRED_SHAPE));
% colormap Jet
% % axis square;
% axis off;
% set(gca,'YDir','normal')
% colorbar('FontSize',16);
% title('Unbiased shape inside pupil (\mum)', 'FontSize',16);
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
end



