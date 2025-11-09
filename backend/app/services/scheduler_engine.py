"""
Smart Scheduler Engine
Implements intelligent scheduling algorithm for device management and battery optimization.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SchedulerEngine:
    """Intelligent scheduler that optimizes device scheduling based on solar forecast."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize scheduler with system configuration.
        
        Args:
            config: System configuration including battery, grid, generator specs
        """
        self.config = config
        self.battery_capacity_kwh = config.get('battery_capacity_kwh', 50.0)
        self.battery_max_charge_kw = config.get('battery_max_charge_rate_kw', 10.0)
        self.battery_max_discharge_kw = config.get('battery_max_discharge_rate_kw', 10.0)
        self.battery_efficiency = config.get('battery_efficiency', 0.95)
        self.battery_min_soc = config.get('battery_min_soc', 0.2)
        self.battery_max_soc = config.get('battery_max_soc', 0.95)
        
        self.grid_peak_rate = config.get('grid_peak_rate_per_kwh', 10.0)
        self.grid_off_peak_rate = config.get('grid_off_peak_rate_per_kwh', 5.0)
        self.grid_peak_hours = config.get('grid_peak_hours', {'start': 8, 'end': 20})
        self.grid_export_rate = config.get('grid_export_rate_per_kwh', 4.0)  # Feed-in tariff rate
        self.grid_export_enabled = config.get('grid_export_enabled', True)
        
        self.generator_fuel_cost = config.get('generator_fuel_cost_per_liter', 80.0)
        self.generator_fuel_consumption = config.get('generator_fuel_consumption_l_per_kwh', 0.25)
        self.generator_max_power = config.get('generator_max_power_kw', 20.0)
        self.generator_min_runtime = config.get('generator_min_runtime_minutes', 30)
        
        self.optimization_mode = config.get('optimization_mode', 'cost')
        self.safety_margin = config.get('safety_margin_critical_loads', 0.1)
    
    def generate_schedule(
        self,
        forecast_data: List[Dict[str, Any]],
        devices: List[Dict[str, Any]],
        initial_battery_soc: float = 0.5,
        time_slot_minutes: int = 10
    ) -> Dict[str, Any]:
        """
        Generate optimized schedule for devices.
        
        Args:
            forecast_data: List of forecast points with solar generation predictions
            devices: List of devices to schedule
            initial_battery_soc: Starting battery state of charge (0-1)
            time_slot_minutes: Duration of each time slot in minutes
            
        Returns:
            Dictionary containing schedule, metrics, and recommendations
        """
        # Filter active devices
        active_devices = [d for d in devices if d.get('is_active', True)]
        
        # Sort devices by priority and type
        sorted_devices = sorted(
            active_devices,
            key=lambda x: (
                0 if x['device_type'] == 'essential' else 1 if x['device_type'] == 'flexible' else 2,
                x['priority_level']
            )
        )
        
        # Initialize schedule
        schedule = []
        current_soc = initial_battery_soc
        battery_energy_kwh = current_soc * self.battery_capacity_kwh
        
        # Track metrics
        total_solar_energy = 0.0
        total_load_energy = 0.0
        total_grid_import = 0.0
        total_grid_export = 0.0
        total_grid_export_revenue = 0.0
        total_generator_energy = 0.0
        generator_runtime = 0.0
        
        # Process each forecast time slot
        for idx, forecast_point in enumerate(forecast_data):
            timestamp = forecast_point.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            solar_generation_kw = forecast_point.get('power_kw', {}).get('mean', 0.0)
            if solar_generation_kw < 0:
                solar_generation_kw = 0.0
            
            # Calculate time slot duration in hours
            slot_duration_hours = time_slot_minutes / 60.0
            
            # Determine which devices should run in this slot
            active_devices_in_slot = self._select_devices_for_slot(
                sorted_devices,
                timestamp,
                forecast_point,
                current_soc,
                solar_generation_kw
            )
            
            # Calculate total load
            total_load_kw = sum(
                device['power_consumption_watts'] / 1000.0
                for device in active_devices_in_slot
            )
            
            # Calculate energy balance
            net_energy_kw = solar_generation_kw - total_load_kw
            
            # Battery operations
            battery_charge_kw = 0.0
            battery_discharge_kw = 0.0
            grid_import_kw = 0.0
            grid_export_kw = 0.0
            generator_power_kw = 0.0
            
            # If we have excess solar, charge battery first, then export to grid
            if net_energy_kw > 0:
                # Charge battery up to max rate
                max_charge_rate = min(
                    self.battery_max_charge_kw,
                    net_energy_kw,
                    (self.battery_max_soc - current_soc) * self.battery_capacity_kwh / slot_duration_hours
                )
                battery_charge_kw = max_charge_rate
                remaining_excess = net_energy_kw - battery_charge_kw
                
                # If still excess and grid export is enabled, sell to grid
                if remaining_excess > 0.01 and self.grid_export_enabled:
                    grid_export_kw = remaining_excess
                    logger.debug(f"Exporting {grid_export_kw:.2f} kW to grid at {timestamp}")
                elif remaining_excess > 0.01:
                    logger.debug(f"Excess solar energy: {remaining_excess:.2f} kW (grid export disabled, wasted)")
            
            # If we have deficit, discharge battery or use grid/generator
            elif net_energy_kw < 0:
                deficit = abs(net_energy_kw)
                
                # First, try to discharge battery
                max_discharge_rate = min(
                    self.battery_max_discharge_kw,
                    (current_soc - self.battery_min_soc) * self.battery_capacity_kwh / slot_duration_hours
                )
                
                if max_discharge_rate > 0 and deficit > 0:
                    battery_discharge_kw = min(max_discharge_rate, deficit)
                    deficit -= battery_discharge_kw
                
                # If still deficit, use grid or generator
                if deficit > 0.01:
                    # Decide between grid and generator based on cost
                    grid_cost = self._get_grid_rate(timestamp) * deficit * slot_duration_hours
                    generator_cost = (deficit * slot_duration_hours * 
                                     self.generator_fuel_consumption * 
                                     self.generator_fuel_cost)
                    
                    if generator_cost < grid_cost and deficit <= self.generator_max_power:
                        generator_power_kw = min(deficit, self.generator_max_power)
                        generator_runtime += slot_duration_hours
                    else:
                        grid_import_kw = deficit
            
            # Update battery SOC
            battery_energy_kwh += (battery_charge_kw * self.battery_efficiency - 
                                  battery_discharge_kw / self.battery_efficiency) * slot_duration_hours
            battery_energy_kwh = max(
                self.battery_min_soc * self.battery_capacity_kwh,
                min(self.battery_max_soc * self.battery_capacity_kwh, battery_energy_kwh)
            )
            current_soc = battery_energy_kwh / self.battery_capacity_kwh
            
            # Accumulate metrics
            total_solar_energy += solar_generation_kw * slot_duration_hours
            total_load_energy += total_load_kw * slot_duration_hours
            total_grid_import += grid_import_kw * slot_duration_hours
            total_grid_export += grid_export_kw * slot_duration_hours
            # Calculate export revenue (using export rate, which is typically lower than import rate)
            export_revenue = grid_export_kw * slot_duration_hours * self.grid_export_rate
            total_grid_export_revenue += export_revenue
            total_generator_energy += generator_power_kw * slot_duration_hours
            
            # Determine power source for each device
            # Calculate how much power each source provides
            total_power_needed = total_load_kw
            solar_used = min(solar_generation_kw, total_power_needed)
            remaining_after_solar = max(0, total_power_needed - solar_used)
            battery_used = min(battery_discharge_kw, remaining_after_solar)
            remaining_after_battery = max(0, remaining_after_solar - battery_used)
            grid_used = min(grid_import_kw, remaining_after_battery)
            generator_used = min(generator_power_kw, max(0, remaining_after_battery - grid_used))
            
            # Create device list with power source information
            devices_with_source = []
            power_allocated = {'solar': 0, 'battery': 0, 'grid': 0, 'generator': 0}
            
            for device in active_devices_in_slot:
                device_power_kw = device['power_consumption_watts'] / 1000.0
                is_irrigation_pump = (
                    device.get('device_type') == 'irrigation' or 
                    'irrigation' in device.get('name', '').lower() or 
                    'pump' in device.get('name', '').lower()
                )
                
                # Determine power source for this device
                # Priority: Solar > Battery > Grid > Generator
                power_source = 'solar'  # Default
                
                if power_allocated['solar'] < solar_used:
                    remaining_solar = solar_used - power_allocated['solar']
                    if device_power_kw <= remaining_solar:
                        power_source = 'solar'
                        power_allocated['solar'] += device_power_kw
                    else:
                        # Partially solar, rest from next source
                        power_source = 'solar'  # Primary source
                        power_allocated['solar'] += remaining_solar
                        device_power_kw -= remaining_solar
                
                if device_power_kw > 0 and power_allocated['battery'] < battery_used:
                    remaining_battery = battery_used - power_allocated['battery']
                    if device_power_kw <= remaining_battery:
                        if power_source == 'solar':
                            power_source = 'solar+battery'  # Mixed source
                        else:
                            power_source = 'battery'
                        power_allocated['battery'] += device_power_kw
                        device_power_kw = 0
                    else:
                        if power_source == 'solar':
                            power_source = 'solar+battery'
                        else:
                            power_source = 'battery'
                        power_allocated['battery'] += remaining_battery
                        device_power_kw -= remaining_battery
                
                if device_power_kw > 0 and power_allocated['grid'] < grid_used:
                    remaining_grid = grid_used - power_allocated['grid']
                    if device_power_kw <= remaining_grid:
                        if power_source in ['solar', 'solar+battery']:
                            power_source = 'solar+grid'
                        elif power_source == 'battery':
                            power_source = 'battery+grid'
                        else:
                            power_source = 'grid'
                        power_allocated['grid'] += device_power_kw
                        device_power_kw = 0
                    else:
                        if power_source in ['solar', 'solar+battery']:
                            power_source = 'solar+grid'
                        elif power_source == 'battery':
                            power_source = 'battery+grid'
                        else:
                            power_source = 'grid'
                        power_allocated['grid'] += remaining_grid
                        device_power_kw -= remaining_grid
                
                if device_power_kw > 0 and power_allocated['generator'] < generator_used:
                    power_source = 'generator'
                    power_allocated['generator'] += device_power_kw
                
                devices_with_source.append({
                    'id': device['id'],
                    'name': device['name'],
                    'power_kw': round(device['power_consumption_watts'] / 1000.0, 2),
                    'power_source': power_source,
                    'is_irrigation_pump': is_irrigation_pump
                })
            
            # Create schedule slot
            schedule.append({
                'time': timestamp.isoformat(),
                'solar_generation_kw': round(solar_generation_kw, 2),
                'total_load_kw': round(total_load_kw, 2),
                'battery_charge_kw': round(battery_charge_kw, 2),
                'battery_discharge_kw': round(battery_discharge_kw, 2),
                'battery_soc': round(current_soc, 3),
                'grid_import_kw': round(grid_import_kw, 2),
                'grid_export_kw': round(grid_export_kw, 2),
                'generator_power_kw': round(generator_power_kw, 2),
                'devices': devices_with_source
            })
        
        # Calculate optimization metrics
        metrics = self._calculate_metrics(
            total_solar_energy,
            total_load_energy,
            total_grid_import,
            total_grid_export,
            total_grid_export_revenue,
            total_generator_energy,
            generator_runtime,
            forecast_data
        )
        
        return {
            'schedule': schedule,
            'metrics': metrics,
            'initial_battery_soc': initial_battery_soc,
            'final_battery_soc': current_soc
        }
    
    def _select_devices_for_slot(
        self,
        devices: List[Dict[str, Any]],
        timestamp: datetime,
        forecast_point: Dict[str, Any],
        current_soc: float,
        available_solar_kw: float
    ) -> List[Dict[str, Any]]:
        """
        Select which devices should run in a given time slot.
        Uses greedy algorithm with priority and constraints.
        Implements intelligent irrigation pump scheduling:
        - Prioritizes irrigation pumps during high solar periods
        - Schedules pumps when solar is available OR when energy is required
        - Delays pumps only if power drop is forecasted AND battery is low
        """
        selected_devices = []
        available_power_kw = available_solar_kw
        
        # Separate devices by type
        essential_devices = [d for d in devices if d['device_type'] == 'essential' and d.get('is_active', True)]
        irrigation_pumps = [
            d for d in devices 
            if d.get('is_active', True) and (
                d.get('device_type') == 'irrigation' or 
                'irrigation' in d.get('name', '').lower() or 
                'pump' in d.get('name', '').lower()
            )
        ]
        flexible_devices = [
            d for d in devices 
            if d['device_type'] in ['flexible', 'optional'] 
            and d.get('is_active', True)
            and not (d.get('device_type') == 'irrigation' or 
                     'irrigation' in d.get('name', '').lower() or 
                     'pump' in d.get('name', '').lower())
        ]
        
        # Check if forecast predicts power drop in next 30-60 minutes
        forecast_power = forecast_point.get('power_kw', {}).get('mean', available_solar_kw)
        power_drop_detected = forecast_power < (available_solar_kw * 0.7)  # 30% drop
        
        # Check if this is a high solar period (solar > 50% of capacity or > 20 kW)
        is_high_solar = available_solar_kw > max(20.0, self.config.get('capacity_kw', 50.0) * 0.5)
        
        hour = timestamp.hour
        
        # Step 1: Add all essential devices (they must run)
        for device in essential_devices:
            device_power_kw = device['power_consumption_watts'] / 1000.0
            selected_devices.append(device)
            available_power_kw -= device_power_kw
        
        # Step 2: Prioritize irrigation pumps during high solar periods
        # Sort irrigation pumps by priority
        irrigation_pumps_sorted = sorted(irrigation_pumps, key=lambda x: x.get('priority_level', 5))
        
        for pump in irrigation_pumps_sorted:
            # Check preferred hours
            preferred = pump.get('preferred_hours')
            if preferred:
                start_hour = preferred.get('start', 0)
                end_hour = preferred.get('end', 24)
                if not (start_hour <= hour < end_hour):
                    continue  # Skip if outside preferred hours
            
            pump_power_kw = pump['power_consumption_watts'] / 1000.0
            
            # Decision logic for irrigation pumps:
            # 1. If high solar period: prioritize irrigation pumps (run on solar)
            # 2. If not high solar but solar available: run if enough solar
            # 3. If low solar but energy required: allow running (will use grid/battery)
            # 4. Delay only if: power drop forecasted AND battery SOC < 40%
            
            should_delay = power_drop_detected and current_soc < 0.4
            
            if should_delay:
                # Delay irrigation pump if power drop is forecasted and battery is low
                logger.debug(f"Delaying irrigation pump {pump.get('name')} due to power drop and low battery")
                continue
            
            # Check if we can run the pump
            essential_buffer = sum(
                d['power_consumption_watts'] / 1000.0
                for d in selected_devices
                if d['device_type'] == 'essential'
            ) * self.safety_margin
            
            # If high solar period, prioritize irrigation pumps (even if slightly over)
            if is_high_solar:
                # During high solar, we can be more aggressive with irrigation pumps
                if available_power_kw - pump_power_kw >= essential_buffer * 0.5:  # Reduced buffer
                    selected_devices.append(pump)
                    available_power_kw -= pump_power_kw
                    logger.debug(f"Scheduling irrigation pump {pump.get('name')} during high solar period")
            elif available_power_kw >= pump_power_kw + essential_buffer:
                # Normal solar period, ensure we have enough with buffer
                selected_devices.append(pump)
                available_power_kw -= pump_power_kw
                logger.debug(f"Scheduling irrigation pump {pump.get('name')} with available solar")
            elif available_power_kw > 0:
                # Low solar but some available - allow pump to run (will supplement with grid/battery)
                # This ensures irrigation happens even if solar is low
                selected_devices.append(pump)
                available_power_kw -= pump_power_kw
                logger.debug(f"Scheduling irrigation pump {pump.get('name')} with low solar (will use grid/battery)")
            else:
                # No solar available, but if irrigation is required, allow it (will use grid/battery)
                # Check if this is within preferred hours and priority is high
                if pump.get('priority_level', 5) <= 2:  # High priority pump
                    selected_devices.append(pump)
                    available_power_kw -= pump_power_kw
                    logger.debug(f"Scheduling high-priority irrigation pump {pump.get('name')} (no solar, using grid/battery)")
        
        # Step 3: Add other flexible/optional devices
        for device in flexible_devices:
            # Check preferred hours
            preferred = device.get('preferred_hours')
            if preferred:
                start_hour = preferred.get('start', 0)
                end_hour = preferred.get('end', 24)
                if not (start_hour <= hour < end_hour):
                    continue  # Skip if outside preferred hours
            
            device_power_kw = device['power_consumption_watts'] / 1000.0
            
            # Check if we have enough power (with safety margin for essential loads)
            essential_buffer = sum(
                d['power_consumption_watts'] / 1000.0
                for d in selected_devices
                if d['device_type'] == 'essential'
            ) * self.safety_margin
            
            if available_power_kw - device_power_kw >= essential_buffer:
                selected_devices.append(device)
                available_power_kw -= device_power_kw
        
        return selected_devices
    
    def _get_grid_rate(self, timestamp: datetime) -> float:
        """Get grid rate for a given timestamp (peak or off-peak)."""
        hour = timestamp.hour
        peak_start = self.grid_peak_hours.get('start', 8)
        peak_end = self.grid_peak_hours.get('end', 20)
        
        if peak_start <= hour < peak_end:
            return self.grid_peak_rate
        return self.grid_off_peak_rate
    
    def _calculate_metrics(
        self,
        total_solar_energy: float,
        total_load_energy: float,
        total_grid_import: float,
        total_grid_export: float,
        total_grid_export_revenue: float,
        total_generator_energy: float,
        generator_runtime_hours: float,
        forecast_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate optimization metrics."""
        total_energy = total_load_energy
        solar_utilization = (total_solar_energy / max(total_energy, 0.01)) * 100 if total_energy > 0 else 0
        
        # Calculate cost savings (including revenue from grid export)
        grid_cost = total_grid_import * self.grid_peak_rate  # Simplified
        generator_cost = (total_generator_energy * 
                          self.generator_fuel_consumption * 
                          self.generator_fuel_cost)
        total_cost = grid_cost + generator_cost - total_grid_export_revenue  # Subtract export revenue
        
        # Baseline cost (if all from grid at peak rate)
        baseline_cost = total_energy * self.grid_peak_rate
        cost_savings = baseline_cost - total_cost
        
        # Battery cycle efficiency (simplified)
        battery_cycle_efficiency = self.battery_efficiency * 100
        
        # Carbon footprint reduction (assuming 0.5 kg CO2 per kWh from grid)
        # Exporting to grid also reduces carbon (replaces grid generation)
        carbon_reduction = (total_solar_energy + total_grid_export) * 0.5
        
        # Grid import reduction
        baseline_grid_import = total_energy
        grid_reduction = ((baseline_grid_import - total_grid_import) / max(baseline_grid_import, 0.01)) * 100
        
        return {
            'solar_utilization_percent': round(solar_utilization, 2),
            'grid_import_reduction_percent': round(grid_reduction, 2),
            'estimated_cost_savings': round(cost_savings, 2),
            'battery_cycle_efficiency': round(battery_cycle_efficiency, 2),
            'carbon_footprint_reduction_kg': round(carbon_reduction, 2),
            'generator_runtime_minutes': round(generator_runtime_hours * 60, 1),
            'total_energy_kwh': round(total_energy, 2),
            'solar_energy_kwh': round(total_solar_energy, 2),
            'grid_energy_kwh': round(total_grid_import, 2),
            'grid_export_energy_kwh': round(total_grid_export, 2),
            'grid_export_revenue': round(total_grid_export_revenue, 2),
            'battery_energy_kwh': round(total_solar_energy - total_load_energy + total_grid_import + total_generator_energy - total_grid_export, 2),
            'generator_energy_kwh': round(total_generator_energy, 2)
        }

