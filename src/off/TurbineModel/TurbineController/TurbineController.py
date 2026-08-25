from __future__ import annotations

from abc import ABC, abstractmethod
import numpy as np

from off.OFFModule import *

class TurbineController(OFFModule):
    """Base interface for local turbine controller.
    Has to potentially cover multiple turbines of one type controller in the same manner but with individual setpoints.
    """
    
    MODULE_TYPE = "TurbineController"
    
    """ 
    ---------------------------------------
    Observables 
    --------------------------------------- 
    """

    @compatibility(CompatibilityLevel.NONE)    
    def obs_power_setpoint_w(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Abstract method to observe the current power setpoint of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.
            t_ids (np.ndarray): Array of turbine IDs.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current power setpoint(s) of the turbine(s) (W).
        """
        raise NotImplementedError
    
    @abstractmethod
    @compatibility(CompatibilityLevel.NONE)
    def obs_yaw_setpoint_deg(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Observes the current yaw misalignment setpoint of the turbine(s).

        Args:
            t_s (np.float64): Current simulation time in seconds.
            t_ids (np.ndarray): Array of turbine IDs.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current yaw setpoint(s) of the turbine(s) (deg).
        """
        raise NotImplementedError
    
    @compatibility(CompatibilityLevel.NONE)   
    def obs_collective_pitch_setpoint_deg(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Observes the current collective pitch setpoint of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.
            t_ids (np.ndarray): Array of turbine IDs.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current collective pitch setpoint(s) of the turbine(s) (deg).
        """
        raise NotImplementedError
    
    @compatibility(CompatibilityLevel.NONE)   
    def obs_individual_pitch_setpoints_deg(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Observes the current individual pitch setpoints of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.
            t_ids (np.ndarray): Array of turbine IDs.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current individual pitch setpoints of the turbine(s) (deg) with shape (n_blades, n_turbines).
        """
        raise NotImplementedError
    
    @compatibility(CompatibilityLevel.NONE)   
    def obs_generator_torque_setpoint_nm(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Observes the current generator torque setpoint of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.
            t_ids (np.ndarray): Array of turbine IDs.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current generator torque setpoint(s) of the turbine(s) (Nm).
        """
        raise NotImplementedError
    
    @compatibility(CompatibilityLevel.NONE)   
    def obs_rotor_torque_setpoint_nm(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Observes the current rotor torque setpoint of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.
            t_ids (np.ndarray): Array of turbine IDs.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current rotor torque setpoint(s) of the turbine(s) (Nm).
        """
        raise NotImplementedError
    
    @compatibility(CompatibilityLevel.NONE)   
    def obs_rotor_speed_setpoint_radps(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Observes the current rotor speed setpoint of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.
            t_ids (np.ndarray): Array of turbine IDs.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current rotor speed setpoint(s) of the turbine(s) (rad/s).
        """
        raise NotImplementedError
    
    @compatibility(CompatibilityLevel.OPTIONAL)   
    def obs_rotor_speed_setpoint_rpm(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Observes the current rotor speed setpoint of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.
            t_ids (np.ndarray): Array of turbine IDs.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current rotor speed setpoint(s) of the turbine(s) (rpm).
        """
        return self.obs_rotor_speed_setpoint_radps(t_s, t_ids) * 60 / (2 * np.pi)

    @compatibility(CompatibilityLevel.NONE)   
    def obs_curtailment_factor(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Observes the current curtailment factor of the turbine. 0 means no curtailment, 1 means full curtailment.

        Args:
            t_s (np.float64): Current simulation time in seconds.
            t_ids (np.ndarray): Array of turbine IDs.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            np.ndarray: Current curtailment factor(s) of the turbine(s) (dimensionless).
        """
        raise NotImplementedError
    
    @compatibility(CompatibilityLevel.NONE)   
    def obs_control_mode(self, t_s: np.float64, t_ids: np.ndarray) -> np.ndarray:
        """ Observes the current control mode of the turbine.

        Args:
            t_s (np.float64): Current simulation time in seconds.

        Raises:
            NotImplementedError: Abstract Method, must be implemented in derived classes.

        Returns:
            str: Current control mode of the turbine(s).
        """
        raise NotImplementedError
