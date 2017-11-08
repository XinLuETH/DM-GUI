% [calib_results, Z_subap_unpow, w_posts_unpow, pitch] = load_calibration_data()
%
% Loads open-loop DM calibration data/fit coefficients for use by 
% open-loop control software. "calib_results" is a cell array that contains
% calibration data and bivariate polynomial surface fit coefficients for
% each actuator of the DM (144 for the Multi-DM). Also loaded is the
% unpowered DM surface figure data "Z_subap_unpow", the unpowered post
% position data "w_posts_unpow" and the DM "pitch". The unpowered surface
% figure data is used to provide absolute DM control, and the DM pitch is
% used for mirror coupling force calculations.

function [calib_results, Z_subap_unpow, w_posts_unpow, pitch] = load_calibration_data()

% Matlab open file dialog
filename = '18W157#032_OPEN_LOOP_CALIBRATION_DATA.mat';
pathname = 'D:\Xin LU\DM\gui_matlab';

% Check to see if calibration data is valid/exists
calib_results = [];
Z_subap_unpow = [];
w_posts_unpow = [];
pitch = [];
if ~isequal(filename,0)
    load(fullfile(pathname, filename),'calib_results','Z_subap_unpow','w_posts_unpow','pitch');  
else
    return;
end

% Show error dialog if data missing
if isempty(calib_results) || isempty(Z_subap_unpow) || isempty(w_posts_unpow) || isempty(pitch)
    calib_results = [];
    Z_subap_unpow = [];
    w_posts_unpow = [];
    pitch = [];
    errordlg('Calibration data not found; Please try again.','File Error');  
end

% To prevent motion of the DM calibration reference plane, three
% actuators at each corner of the active aperture remain un-energized during
% calibration. These actuators (2,13,14,11,23,24,121,122,134,131,132,143) 
% can still be used by defining their calibration information to that of
% neighboring actuators.
calib_results{2} = calib_results{3};
calib_results{13} = calib_results{25};
calib_results{14} = calib_results{27};

calib_results{11} = calib_results{10};
calib_results{23} = calib_results{34};
calib_results{24} = calib_results{36};

calib_results{121} = calib_results{109};
calib_results{122} = calib_results{111};
calib_results{134} = calib_results{135};

calib_results{131} = calib_results{118};
calib_results{132} = calib_results{120};
calib_results{143} = calib_results{142};