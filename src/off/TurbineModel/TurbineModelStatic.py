from __future__ import annotations
import numpy as np
from abc import ABC, abstractmethod

from off.OFFModule import*
from .TurbineModel import TurbineModel
from off.WakeModel import WakeModel
from off.TurbineModel.TurbineController import TurbineController
from off.AtmosphericModel import AtmosphericModel

class TurbineModelStatic(TurbineModel):
    """ 
        Temporary Placeholder for a static turbine that maximizes power extraction from the wind.
    """

    REQUIRES = {
        'WakeModel': {
            'obs_horizontal_wind_speed_and_dir_mps_deg': CompatibilityLevel.OPTIONAL,
            'obs_horizontal_wind_direction_deg': CompatibilityLevel.OPTIONAL,
            'obs_horizontal_wind_speed_mps': CompatibilityLevel.OPTIONAL
        }
    }
    
    def __init__(self, settings: dict, turbine_controller: TurbineController):
        super().__init__()
        self.settings = settings
        self.turbine_controller = turbine_controller

        # Constants
        self.const_n_turbines = len(settings["base_locations_m"])
        self.const_rotor_points_xyz_m       = self._generate_rotor_points_xyz(settings["rotor_discretization_points"], settings["rotor_discretization_type"]) * settings["turbine"]["D_m"]
        self.const_Cp_u_values = settings["turbine"]["performance"]["Cp_u_values"]
        self.const_Cp_u_wind_speeds_mps = settings["turbine"]["performance"]["Cp_u_wind_speeds_mps"]
        self.const_Ct_u_values = settings["turbine"]["performance"]["Ct_u_values"]
        self.const_Ct_u_wind_speeds_mps = settings["turbine"]["performance"]["Ct_u_wind_speeds_mps"]

        # States
        self.state_rotor_center_location_m  = self.const_base_locations_m + np.array([0.0, 0.0, settings["turbine"]["hub_height_m"]])

        # Measurements / observations
        self.state_rotor_effective_wind_speed_mps       = np.full(self.const_n_turbines, 0.0, dtype=float)
        self.state_rotor_effective_wind_direction_deg   = np.full(self.const_n_turbines, 0.0, dtype=float)
        self.meas_air_density_kgpm3 = 1.0

        # Controller
        self.turbine_controller = TurbineController(settings["turbine_controller"])

    def step(self, wake_model: WakeModel, atmospheric_model: AtmosphericModel, t_s: np.float64):
        """ Steps the turbine model forward in time.

        Args:
            wake_model (WakeModel): The wake model to use for calculating the effective wind speed and direction at the rotor.
            atmospheric_model (AtmosphericModel): The atmospheric model to get the air density.
            t_s (np.float64): The current simulation time in seconds.
        """
        self.meas_air_density_kgpm3 = atmospheric_model.obs_air_density_kgpm3(self.state_rotor_center_location_m[:,0].reshape(-1, 1), t_s)

        for i in range(self.const_n_turbines):
            # Get environmental wind speed and direction at rotor center locations
            # TODO need to be oriented based on yaw orientation
            rotor_points_xyz_m = self.state_rotor_center_location_m[i] + self.const_rotor_points_xyz_m
            # Get effective wind speed and direction at rotor center locations
            self.state_rotor_effective_wind_speed_mps[i]        = wake_model.obs_horizontal_wind_speed_mps(rotor_points_xyz_m.T, t_s)
            self.state_rotor_effective_wind_direction_deg[i]    = wake_model.obs_horizontal_wind_dir_deg(rotor_points_xyz_m.T, t_s)

        # Call controller to determine new yaw orientation
        self.state_rotor_yaw_angle_deg = self.turbine_controller.obs_yaw_setpoint_deg(t_s, np.arange(self.const_n_turbines))




    """ 
    ---------------------------------------
    Observables 
    --------------------------------------- 
    """

    """ 
    General
    --------------------------------------- 
    """
    @compatibility(CompatibilityLevel.FULL)
    def obs_num_turbines(self) -> int:
        """ Observes the number of turbines in the farm.

        Returns:
            int: Number of turbines in the farm.
        """
        return self.const_n_turbines

    @compatibility(CompatibilityLevel.FULL)
    def obs_turbine_type(self) -> str:
        """ Observes the type of turbine in the farm.

        Returns:
            str: Type of turbine in the farm.
        """
        return self.settings["turbine"]["name"]

    """ 
    Power 
    --------------------------------------- 
    """

    @compatibility(CompatibilityLevel.FULL)
    def obs_generator_power_w(self, t_s: np.float64) -> np.float64:
        """ Observes the current generator power of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.

        
        Returns:
            np.ndarray: Current generator power output of the turbine(s) (W).
        """

        p = (0.5 * self.meas_air_density_kgpm3 * np.pi * (self.settings["turbine"]["D_m"] / 2) ** 2 
            * self.state_rotor_effective_wind_speed_mps ** 3 
            * self.const_Cp_u_values[np.searchsorted(self.const_Cp_u_wind_speeds_mps, self.state_rotor_effective_wind_speed_mps, side='right') - 1] 
            * np.cos(np.radians(self.state_rotor_yaw_angle_deg)) ** self.settings["turbine"]["performance"]["pP"]
            * self.settings["turbine"]["performance"]["eta_g"]
        )
        return p

    @compatibility(CompatibilityLevel.OPTIONAL)
    def obs_aerodynamic_power_w(self, t_s: np.float64) -> np.ndarray:
        """ Observes the current aerodynamic power of the turbine.
        The aerodynamic power is the power extracted from the wind by the rotor, which is then converted to electrical power by the generator, coupled by a potential gearbox.

        Args:
            t_s (np.float64): Current simulation time in seconds.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current aerodynamic power of the turbine(s) (W).
        """
        return self.obs_generator_power_w(t_s) / self.settings["turbine"]["performance"]["eta_g"]

    @compatibility(CompatibilityLevel.OPTIONAL)
    def obs_available_power_w(self, t_s: np.float64) -> np.ndarray:
        """ Observes the current available power of the turbine.
        The available power is the power that would be generated if the turbine were operating at its optimal conditions, given the current wind speed and direction.

        Args:
            t_s (np.float64): Current simulation time in seconds.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current available power of the turbine(s) (W).
        """
        raise self.obs_generator_power_w(t_s)

    @compatibility(CompatibilityLevel.FULL)    
    def obs_power_coefficient(self, t_s: np.float64) -> np.ndarray:
        """ Observes the current power coefficient of the turbine.
        The power coefficient is a dimensionless number that represents the efficiency of the turbine in converting the kinetic energy of the wind into electrical energy.

        Args:
            t_s (np.float64): Current simulation time in seconds.

        Returns:
            np.ndarray: Current power coefficient of the turbine(s) (dimensionless).
            
        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.
        """
        return (self.const_Cp_u_values[np.searchsorted(self.const_Cp_u_wind_speeds_mps, self.state_rotor_effective_wind_speed_mps, side='right') - 1] 
                * np.cos(np.radians(self.state_rotor_yaw_angle_deg)) ** self.settings["turbine"]["performance"]["pP"])

    @compatibility(CompatibilityLevel.NONE)   
    def obs_power_curve(self, t_s: np.float64) -> np.ndarray:
        """ Observes the current power curve of the turbine.
        The power curve is a function that describes the relationship between the wind speed and the power output of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.
        
        Returns:
            np.ndarray: Current power curve (W) of the turbine type as a function of wind speed (m/s) in the shape (n x 2) where the first column is wind speed and the second column is power output.
        """
        return np.column_stack((self.const_Cp_u_wind_speeds_mps, 
            0.5 * self.meas_air_density_kgpm3 * np.pi * (self.settings["turbine"]["D_m"] / 2) ** 2 
            * self.const_Cp_u_wind_speeds_mps ** 3 
            * self.const_Cp_u_values 
            * self.settings["turbine"]["performance"]["eta_g"]
        ))  

    
    """ 
    Private Methods 
    --------------------------------------- 
    """

    def _generate_rotor_points_xyz(self, n_points: int, discretization_type: str, tilt_deg: float) -> np.ndarray:
        """ Generates the rotor points in Cartesian coordinates (-) based on the specified discretization type.
        The points are mainly distributed in the y,z plane with x only used for tilt.

        Args:
            n_points (int): Number of rotor points to generate.
            discretization_type (str): Type of discretization ('isocell', 'uniform', etc.).
            tilt_deg (float): Tilt angle of the rotor in degrees.

        Returns:
            np.ndarray: Array of shape (4, n_points) containing the rotor points in Cartesian coordinates (-), as well as the weights.

        """
        if discretization_type == "isocell": # TODO: Implement isocell discretization
            raise NotImplementedError
            # Placeholder for isocell discretization logic
            # This should be replaced with actual implementation
            theta = np.linspace(0, 2 * np.pi, n_points)
            r = np.sqrt(np.random.rand(n_points))  # Random radius for isocell distribution
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            z = np.zeros(n_points)  # Assuming rotor plane at z=0
            weights = np.ones(n_points) / n_points  # Uniform weights
            return np.vstack((x, y, z, weights))
        else:
            raise ValueError(f"Discretization type '{discretization_type}' is not supported.")