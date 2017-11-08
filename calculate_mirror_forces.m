% [Fm, q] = calculate_mirror_forces(DESIRED_SHAPE,num_subaps,pitch)
%
% Calculates the mirror coupling forces "Fm" associated with an input shape
% "DESIRED_SHAPE" (w(x,y)) using the thin plate equation. "num_subaps"
% represents the width of the desired shape and "pitch" corresponds to the
% actuator post separation, which is a square grid. The return value "q"
% corresponds to the mirror pressure (q(x,y)) exerted on the plate which is
% required to produce the desired shape. The mirror coupling force "Fm" is
% estimated by integrating the mirror pressure over each DM subaperture.

function [Fm, q] = calculate_mirror_forces(DESIRED_SHAPE,num_subaps,pitch)
    t = 3e-6; % mirror thickness 
    nu = 0.22; % Poisson's ratio
    E = 165.7e9; % Young's Modulus for PolySi
    D = (E*t^3)/(12*(1-nu^2)); % Flexural rigidity of mirror
    h = num_subaps*pitch/length(DESIRED_SHAPE); %distance between pixels
    
    % Apply Matlab gradient functions to differentiate the input shape
    % as described by the thin plate equation in order to determine the 
    % corresponding mirror pressure
    [dz_dx, dz_dy] = gradient(DESIRED_SHAPE,h);
    [d2z_dx2, d2z_dxdy] = gradient(dz_dx,h);
    [d2z_dy2, d2z_dydx] = gradient(dz_dy,h);
    f = D*4*del2(4*del2(DESIRED_SHAPE,h),h) - 6*D/t^2*(dz_dx.^2.*d2z_dx2 + dz_dy.^2.*d2z_dy2);
    q = f*(h)^2;  % Mirror facesheet pressure

    % Integrate the pressure over each DM subaperture to estimate the
    % coupling force for each actuator of the DM. Currently implemented as
    % a nested for loop, which is not very efficient.
    bin_size2=length(q)/num_subaps;
    Fm = zeros(num_subaps,num_subaps);
    for ii = 1:num_subaps
        for jj = 1:num_subaps
            Fm(ii,jj)=sum(sum(q(((ii-1)*bin_size2+1):ii*bin_size2,((jj-1)*bin_size2+1):jj*bin_size2)));
        end
    end
end

