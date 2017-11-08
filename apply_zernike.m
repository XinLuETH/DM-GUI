function [DESIRED_SHAPE, VOLTAGE_MAP] = apply_zernike(coeffcient)

subap_pixel_width = 21;              % Number of pixels across DM subaperture
DM_subap_width = 12;            % Number of DM subapertures in Multi-DM
zernike_subap_width = 9;        % Size of Zernike pupil, in subapertures  
                                      % this is 9 actuators across
amplitude = 1e-9; %750e-9;                   % Zernike amplitude, peak to valley is 2*amplitude 

offset = 1.5e-6;                        % represents a piston bias below the DM reference plane

% n and m for the first 15 Zernike fucntions
% n = [0  1  1  2  2 2  3 3  3 3 4 4  4 4  4];
% m = [0  1 -1  0 -2 2 -1 1 -3 3 0 2 -2 4 -4];
n = [0  1  1  2  2 2  3 3  3 3 4 4  4 4  4  5 5  5 5  5 5 6  6 6  6 6  6 6];
m = [0  1 -1  0 -2 2 -1 1 -3 3 0 2 -2 4 -4 -1 1 -3 3 -5 5 0 -2 2 -4 4 -6 6];
% n = [0  1  1  2  2  2  3  3  3  3  4  4 4 4 4];
% m = [0 -1  1 -2  0  2 -3 -1  1  3 -4 -2 0 2 4];
%% create the first 15 Zernike fucntions
% Create the desired Zernike shape inside a pupil measuring 9 subapertures 
% in diameter

% determine array index that corresponds to Zernike pupil                                      
index = DM_subap_width/zernike_subap_width;
num_points = subap_pixel_width*DM_subap_width;
i1 = -index;
i2 = index;
   
% Use "zernfun" function to create Zernike polynomial of input orders
[xi,yi] = meshgrid(linspace(i1,i2,num_points),linspace(i1,i2,num_points));
[qi,ri] = cart2pol(xi,yi);
IOI = ri<=1;
    
% Fill area beyond Zernike pupil with NaNs
zi = zeros(size(xi))+ NaN;
    
% "zerfun" in as open-source function available on Mathwork's Central
k = zernfun(n,m,ri(IOI),qi(IOI));

sum_zernike = zeros(size(ri(IOI)));

% the Zernike term is 28th, but the GUI uses only the first 15th, the if
% senstence below adds 0 zeros to the coefficient from the GUI
if length(coeffcient)<length(n)
    coeffcient(numel(n))=0;
end

piston = coeffcient(1)*amplitude;% * k(:,1);(IOI)
for i = 2:length(n)
    sum_zernike = sum_zernike + amplitude * coeffcient(i) * k(:,i);
end

zi(IOI) = sum_zernike;

BW_PUPIL = ri <=1;
PUPIL_IND = find(BW_PUPIL==1);

% Offset the midpoint plane for the Zernike shape "zi" to about half of 
% the DM actuator stroke, defining the desired shape inside the pupil 
DESIRED_SHAPE = (zi - (max(zi(PUPIL_IND))+ min(zi(PUPIL_IND)))/2 - offset + piston);
% DESIRED_SHAPE = zi - offset ;

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

% imagesc(1e9*(DESIRED_SHAPE));
% colormap Jet
% % axis square;
% % axis off;
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
%% Step 4: Apply predicted voltage map to DM 

% MultiDM driver channel to actuator mapping
%driver_map_ID = 2;

% Open connection to the DM driver electronics. The "driver_info" structure
% is used by all BMC Matlab control functions. Open and close operations
% need only be performed once for each program instance.
%[error_code, driver_info] = OPEN_multiDM(driver_map_ID);

% Apply open loop voltage map to the DM, after first reshaping from a 144x1
% array into a 12x12 array. This function can be called repeatedly after 
% opening and before closing the driver connection.
%UPDATE_multiDM(driver_info, reshape(VOLTAGE_MAP',numel(VOLTAGE_MAP),1));
 
end
